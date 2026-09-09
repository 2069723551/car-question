# ============================================================
# 文件路径：car-sales-backend/services/ranking_service.py
# 作用：厂商销量排行榜聚合服务（中国市场）
#   数据源：data/china_car_sales.csv
#     （中国乘用车月度销量，源自乘联会 CPCA 登记记录整理，2018-2024，38806 条）
#   聚合：累计 TOP10 / 年度趋势 / 年度榜单 / 市场占比 / 新能源占比
# ============================================================

import pathlib

import pandas as pd

DATA_DIR = pathlib.Path(__file__).resolve().parent.parent / "data"
CSV_PATH = DATA_DIR / "china_car_sales.csv"


def _load() -> pd.DataFrame:
    df = pd.read_csv(CSV_PATH)
    df.columns = [c.strip() for c in df.columns]
    df["ym"] = pd.to_datetime(df["year_month"], errors="coerce")
    df["Year"] = df["ym"].dt.year
    df["units_sold"] = pd.to_numeric(df["units_sold"], errors="coerce")
    return df.dropna(subset=["Year", "units_sold"])


def get_ranking_data() -> dict:
    """返回排行榜全部数据（累计榜单 / 年度榜单 / 趋势 / 占比）"""
    df = _load()

    total_qty = int(df["units_sold"].sum())

    # 1. 累计 TOP10 厂商（全期销量 + 占比）
    cumulative = (
        df.groupby("make")["units_sold"]
        .sum()
        .sort_values(ascending=False)
        .head(10)
        .reset_index()
    )
    top10_sum = int(cumulative["units_sold"].sum())
    cumulative_top = [
        {
            "brand": str(r["make"]),
            "total": int(r["units_sold"]),
            "share": round(float(r["units_sold"]) / total_qty * 100, 1),
            "share_in_top": round(float(r["units_sold"]) / top10_sum * 100, 1),
        }
        for _, r in cumulative.iterrows()
    ]

    # 2. TOP6 厂商年度销量趋势（多线图）
    top6 = list(cumulative["make"].head(6))
    trend_rows = (
        df[df["make"].isin(top6)]
        .groupby(["Year", "make"])["units_sold"]
        .sum()
        .reset_index()
    )
    years = sorted(trend_rows["Year"].unique())
    trend_series = [
        {
            "year": int(y),
            "brands": {
                str(r["make"]): int(r["units_sold"])
                for _, r in trend_rows[trend_rows["Year"] == y].iterrows()
            },
        }
        for y in years
    ]

    # 3. 逐年销量冠军（年度王座演变）
    annual = (
        df.groupby(["Year", "make"])["units_sold"]
        .sum()
        .reset_index()
        .sort_values(["Year", "units_sold"], ascending=[True, False])
    )
    champions = []
    for y, g in annual.groupby("Year"):
        row = g.iloc[0]
        champions.append(
            {
                "year": int(y),
                "brand": str(row["make"]),
                "total": int(row["units_sold"]),
                "runner_up": str(g.iloc[1]["make"]) if len(g) > 1 else None,
            }
        )

    # 4. 最新完整年度 TOP10（取 12 个月齐全的最后一年）
    month_cnt = df.groupby("Year")["ym"].nunique()
    full_years = month_cnt[month_cnt >= 12].index
    latest_year = int(max(full_years)) if len(full_years) > 0 else int(df["Year"].max())
    latest = (
        df[df["Year"] == latest_year]
        .groupby("make")["units_sold"]
        .sum()
        .sort_values(ascending=False)
        .head(10)
        .reset_index()
    )
    latest_top = [
        {"brand": str(r["make"]), "total": int(r["units_sold"])}
        for _, r in latest.iterrows()
    ]

    # 5. 新能源（EV）销量占比
    ev_total = int(df[df["is_ev"] == "EV"]["units_sold"].sum())
    ev_share = round(ev_total / total_qty * 100, 1) if total_qty else 0

    # 6. 指标卡
    stats = {
        "years": f"{int(df['Year'].min())}-{int(df['Year'].max())}",
        "brands": int(df["make"].nunique()),
        "total_sales": total_qty,
        "top_brand": cumulative_top[0]["brand"] if cumulative_top else "-",
        "top_brand_sales": cumulative_top[0]["total"] if cumulative_top else 0,
        "latest_year": latest_year,
        "ev_share": ev_share,
    }

    return {
        "cumulative_top": cumulative_top,
        "trend_series": trend_series,
        "champions": champions,
        "latest_top": latest_top,
        "stats": stats,
    }
