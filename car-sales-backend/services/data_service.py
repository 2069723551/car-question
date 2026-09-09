# ============================================================
# 文件路径：car-sales-backend/services/data_service.py
# 说明：加载中国乘用车销量数据，返回结构化数据
#   主序列：data/china_monthly.csv（月度总销量 2018-2024）
#   明细：data/china_car_sales.csv（车型-月度销量，乘联会 CPCA 来源）
# ============================================================

import pandas as pd

from core.config import DATA_DIR, MAIN_CSV, MVA_CSV


def load_main_series() -> pd.DataFrame:
    """加载主数据集（china_monthly：2018-01 ~ 2024-04 月度总销量）"""
    path = DATA_DIR / MAIN_CSV
    df = pd.read_csv(path)
    df.columns = ["date", "sales"]  # 统一列名
    df["date"] = pd.to_datetime(df["date"])
    return df


def load_mva_series() -> pd.DataFrame:
    """加载明细数据并按年月聚合新能源(EV)/燃油车 月度销量"""
    path = DATA_DIR / MVA_CSV
    df = pd.read_csv(path)
    df.columns = [c.strip() for c in df.columns]
    df["ym"] = pd.to_datetime(df["year_month"], errors="coerce")
    df["units_sold"] = pd.to_numeric(df["units_sold"], errors="coerce")
    df = df.dropna(subset=["ym", "units_sold"])
    df["date"] = df["ym"].dt.to_period("M").dt.to_timestamp()
    df["kind"] = df["is_ev"].map(lambda x: "EV" if x == "EV" else "fuel")
    piv = (
        df.pivot_table(index="date", columns="kind", values="units_sold", aggfunc="sum")
        .fillna(0)
        .reset_index()
    )
    for col in ("EV", "fuel"):
        if col not in piv.columns:
            piv[col] = 0
    return piv.rename(columns={"EV": "new", "fuel": "used"})


def load_china_detail() -> pd.DataFrame:
    """加载完整明细数据（车型-月度销量）"""
    path = DATA_DIR / MVA_CSV
    df = pd.read_csv(path)
    df.columns = [c.strip() for c in df.columns]
    df["ym"] = pd.to_datetime(df["year_month"], errors="coerce")
    df["Year"] = df["ym"].dt.year
    df["Month"] = df["ym"].dt.month
    df["units_sold"] = pd.to_numeric(df["units_sold"], errors="coerce")
    df["low_price"] = pd.to_numeric(df["low_price"], errors="coerce")
    return df.dropna(subset=["ym", "units_sold"])


def get_overview() -> dict:
    """数据集概览：记录数、时间范围、统计量"""
    main_df = load_main_series()
    detail_df = load_china_detail()
    return {
        "main": {
            "name": "china_monthly",
            "records": int(len(main_df)),
            "start": str(main_df["date"].min().date()),
            "end": str(main_df["date"].max().date()),
            "mean": round(float(main_df["sales"].mean())),
            "std": round(float(main_df["sales"].std())),
            "min": int(main_df["sales"].min()),
            "max": int(main_df["sales"].max()),
        },
        "mva": {
            "name": "china_car_sales",
            "records": int(len(detail_df)),
            "start": f"{int(detail_df['Year'].min())}-01",
            "end": f"{int(detail_df['Year'].max())}-12",
        },
    }


def get_main_series_json() -> list:
    """主序列：[{date, sales}]"""
    df = load_main_series()
    return [
        {"date": str(row["date"].date()), "sales": int(row["sales"])}
        for _, row in df.iterrows()
    ]


def get_mva_series_json() -> list:
    """新能源/燃油月度序列：[{date, new, used}]"""
    df = load_mva_series()
    return [
        {"date": str(row["date"].date()), "new": int(row["new"]), "used": int(row["used"])}
        for _, row in df.iterrows()
    ]
