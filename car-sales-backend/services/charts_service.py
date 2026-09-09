# ============================================================
# 文件路径：car-sales-backend/services/charts_service.py
# 作用：数据图集聚合接口（供数据可视化大屏展示）
#   数据源：中国乘用车销量（乘联会 CPCA 来源，2018-2024，38806 条）
#   聚合出 12 组图表数据：月度趋势 / 新能源vs燃油 / 年度销量 /
#   季节模式 / 移动平均 / 同比增速 / 车型分布 / 堆叠对比 /
#   新能源渗透率 / 厂商占比 / 价格带分布 / 国产vs外资
# ============================================================

import pandas as pd

from services.data_service import load_main_series, load_mva_series, load_china_detail


def get_chart_data() -> dict:
    """返回全部图集数据（一次拉取，前端渲染多张图表）"""
    main_df = load_main_series()      # 月度总销量
    ev_df = load_mva_series()         # EV/燃油 月度销量
    detail = load_china_detail()      # 车型-月度明细

    # ---------- 1. 年度销量（完整年份 2018-2023） ----------
    main_df["year"] = main_df["date"].dt.year
    month_cnt = main_df.groupby("year")["date"].count()
    full_years = month_cnt[month_cnt >= 12].index
    annual = (
        main_df[main_df["year"].isin(full_years)]
        .groupby("year")["sales"]
        .sum()
        .reset_index()
        .rename(columns={"sales": "total"})
    )
    annual_sales = [
        {"year": int(r["year"]), "total": int(r["total"])}
        for _, r in annual.iterrows()
    ]

    # ---------- 2. 月度季节模式（1-12 月多年平均） ----------
    main_df["month"] = main_df["date"].dt.month
    seasonal = (
        main_df.groupby("month")["sales"]
        .mean()
        .reset_index()
        .rename(columns={"sales": "avg"})
    )
    seasonal_pattern = [
        {"month": int(r["month"]), "avg": round(float(r["avg"]))}
        for _, r in seasonal.iterrows()
    ]

    # ---------- 3. 移动平均（12 个月）vs 原始值 ----------
    main_sorted = main_df.sort_values("date").reset_index(drop=True)
    ma = main_sorted["sales"].rolling(12).mean()
    moving_average = [
        {
            "date": str(r["date"].date()),
            "sales": int(r["sales"]),
            "ma12": round(float(ma[i])) if not pd.isna(ma[i]) else None,
        }
        for i, (_, r) in enumerate(main_sorted.iterrows())
    ]

    # ---------- 4. 年度同比增速 ----------
    annual_sorted = annual.sort_values("year").reset_index(drop=True)
    growth_rows = []
    prev = None
    for _, r in annual_sorted.iterrows():
        g = None
        if prev is not None and prev > 0:
            g = round((r["total"] - prev) / prev * 100, 1)
        growth_rows.append({"year": int(r["year"]), "total": int(r["total"]), "growth": g})
        prev = r["total"]
    yoy_growth = growth_rows

    # ---------- 5. 车型月销量分布直方图（车型-月记录数） ----------
    bins = [0, 5000, 10000, 15000, 20000, 30000, 40000, 60000, 10**9]
    labels = ["0-5千", "5千-1万", "1万-1.5万", "1.5万-2万", "2万-3万", "3万-4万", "4万-6万", "6万以上"]
    hist = (
        pd.cut(detail["units_sold"], bins=bins, labels=labels, right=False)
        .value_counts()
        .sort_index()
        .reindex(labels)
        .fillna(0)
    )
    distribution = [
        {"range": lb, "count": int(hist.get(lb, 0))} for lb in labels
    ]

    # ---------- 6. 新能源(EV) vs 燃油车（按年，堆叠/对比） ----------
    ev_df["year"] = ev_df["date"].dt.year
    ev_agg = (
        ev_df.groupby("year")[["new", "used"]]
        .sum()
        .reset_index()
    )
    mva_compare = [
        {"year": int(r["year"]), "new": int(r["new"]), "used": int(r["used"])}
        for _, r in ev_agg.iterrows()
    ]

    # ---------- 7. 新能源渗透率年度走势（%） ----------
    ev_agg["total"] = ev_agg["new"] + ev_agg["used"]
    ev_agg["share_new"] = (ev_agg["new"] / ev_agg["total"] * 100).round(1)
    ev_agg["share_used"] = 100 - ev_agg["share_new"]
    mva_sales_trend = [
        {"year": int(r["year"]), "new": float(r["share_new"]), "used": float(r["share_used"])}
        for _, r in ev_agg.iterrows()
    ]

    # ---------- 8. 厂商销量占比（TOP6 + 其他，环形图） ----------
    make_sum = detail.groupby("make")["units_sold"].sum().sort_values(ascending=False)
    top6 = make_sum.head(6)
    other = make_sum.iloc[6:].sum()
    mva_share = [
        {"name": str(k), "value": int(v)} for k, v in top6.items()
    ] + [{"name": "其他", "value": int(other)}]

    # ---------- 9. 国产 vs 外资品牌销量走势（按年，万辆） ----------
    detail["price_wan"] = detail["low_price"] / 10.0  # 千元 -> 万元
    bc = detail.copy()
    bc["domestic"] = bc["brand_country"].map(lambda x: "domestic" if x == "China" else "foreign")
    bc_year = (
        bc.groupby(["Year", "domestic"])["units_sold"]
        .sum()
        .unstack(fill_value=0)
        .reset_index()
    )
    for col in ("domestic", "foreign"):
        if col not in bc_year.columns:
            bc_year[col] = 0
    bc_year = bc_year[bc_year["Year"].isin(full_years)]
    avg_price_trend = [
        {
            "year": int(r["Year"]),
            "new": round(float(r["domestic"]) / 1e4, 1),
            "used": round(float(r["foreign"]) / 1e4, 1),
        }
        for _, r in bc_year.iterrows()
    ]

    # ---------- 10. 价格带分布（按 low_price，万元） ----------
    price_bins = [0, 10, 15, 20, 30, 10**9]
    price_labels = ["10万以下", "10-15万", "15-20万", "20-30万", "30万以上"]
    detail["band"] = pd.cut(
        detail["price_wan"], bins=price_bins, labels=price_labels, right=False
    )
    band = (
        detail.groupby("band", observed=True)["units_sold"]
        .sum()
        .reindex(price_labels)
        .fillna(0)
    )
    price_bands = [
        {"band": lb, "count": int(band.get(lb, 0))} for lb in price_labels
    ]

    # ---------- 指标卡 ----------
    ev_total = int(ev_df["new"].sum())
    fuel_total = int(ev_df["used"].sum())
    stats = {
        "main_total": int(main_df["sales"].sum()),
        "main_avg": round(float(main_df["sales"].mean())),
        "main_peak": {
            "date": str(main_df.loc[main_df["sales"].idxmax(), "date"].date()),
            "sales": int(main_df["sales"].max()),
        },
        "main_trough": {
            "date": str(main_df.loc[main_df["sales"].idxmin(), "date"].date()),
            "sales": int(main_df["sales"].min()),
        },
        "mva_new_total": ev_total,
        "mva_used_total": fuel_total,
    }

    return {
        "annual_sales": annual_sales,
        "seasonal_pattern": seasonal_pattern,
        "moving_average": moving_average,
        "yoy_growth": yoy_growth,
        "distribution": distribution,
        "mva_compare": mva_compare,
        "mva_sales_trend": mva_sales_trend,
        "mva_share": mva_share,
        "avg_price_trend": avg_price_trend,
        "price_bands": price_bands,
        "stats": stats,
    }
