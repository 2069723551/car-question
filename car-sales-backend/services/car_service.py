# ============================================================
# 文件路径：car-sales-backend/services/car_service.py
# 说明：选车助手 / 车型排行 / 数据浏览 服务
#   数据：data/china_car_sales.csv（车型-月度销量，乘联会 CPCA 来源）
#   价格：low_price 单位千元，÷10 转为万元
# ============================================================

from functools import lru_cache

import pandas as pd

from core.config import DATA_DIR, MVA_CSV

BODY_LABELS = {
    "Sedan": "轿车",
    "SUV": "SUV",
    "MPV": "MPV",
    "Hatchback": "两厢车",
    "Sports Car": "跑车",
}
COUNTRY_LABELS = {
    "China": "国产",
    "Germany": "德系",
    "Japan": "日系",
    "United States": "美系",
    "South Korea": "韩系",
    "France": "法系",
    "Italy": "意系",
    "Sweden": "瑞典",
    "Czech Republic": "捷克",
    "United Kingdom": "英系",
}


@lru_cache(maxsize=1)
def load_detail() -> pd.DataFrame:
    """加载车型-月度销量明细（带缓存，首次读取后常驻内存）"""
    df = pd.read_csv(DATA_DIR / MVA_CSV)
    df.columns = [c.strip() for c in df.columns]
    df["ym"] = pd.to_datetime(df["year_month"], errors="coerce")
    df["price_wan"] = pd.to_numeric(df["low_price"], errors="coerce") / 10  # 千元 → 万元
    df["units_sold"] = pd.to_numeric(df["units_sold"], errors="coerce")
    df = df.dropna(subset=["ym", "units_sold"])
    return df


def get_meta() -> dict:
    """筛选表单元数据：厂商列表、车身类型、价格范围、品牌国别"""
    df = load_detail()
    makes = sorted(df["make"].dropna().unique().tolist())
    return {
        "makes": makes,
        "body_types": [
            {"value": b, "label": BODY_LABELS.get(b, b)} for b in sorted(df["body_type"].dropna().unique())
        ],
        "countries": [
            {"value": c, "label": COUNTRY_LABELS.get(c, c)} for c in sorted(df["brand_country"].dropna().unique())
        ],
        "price_min": 0,
        "price_max": round(float(df["price_wan"].max()), 1),
    }


def safe(v, default='-'):
    return v if (v is not None and str(v) != 'nan') else default


def _model_agg(sub: pd.DataFrame) -> pd.DataFrame:
    """按车型聚合统计（总销量 / 价格 / 厂商 / 最近月销量）"""
    last = sub.sort_values("ym").drop_duplicates("model", keep="last")
    g = sub.groupby("model").agg(
        make=("make", "first"),
        total=("units_sold", "sum"),
        avg_price=("price_wan", "mean"),
        min_price=("price_wan", "min"),
        max_price=("price_wan", "max"),
        brand_country=("brand_country", "first"),
        is_ev=("is_ev", "first"),
        body_type=("body_type", "first"),
        months=("ym", "nunique"),
    )
    g["last_ym"] = last.set_index("model")["ym"]
    g["last_sold"] = last.set_index("model")["units_sold"]
    return g.reset_index()


def recommend(budget_min=None, budget_max=None, energy="all", body="all", country="all", limit=12) -> list:
    """选车推荐：按预算/能源/车身/国别筛选，按累计销量热度排序"""
    df = load_detail()
    m = df.copy()
    if budget_min is not None:
        m = m[m["price_wan"] >= budget_min]
    if budget_max is not None:
        m = m[m["price_wan"] <= budget_max]
    if energy in ("EV", "Gasoline"):
        m = m[m["is_ev"] == energy]
    if body and body != "all":
        m = m[m["body_type"] == body]
    if country and country != "all":
        m = m[m["brand_country"] == country]
    if m.empty:
        return []
    agg = _model_agg(m).sort_values("total", ascending=False).head(limit)
    return _to_json(agg)


def top(period="total", limit=20) -> dict:
    """车型销量 TOP 榜：period=total|latest|年份"""
    df = load_detail()
    if period == "latest":
        ym_max = df["ym"].max()
        sub = df[df["ym"] == ym_max]
        label = str(ym_max.date())[:7]
    elif period.isdigit():
        sub = df[df["ym"].dt.year == int(period)]
        label = period + " 年"
    else:
        sub = df
        label = "2018-2024 累计"
    if sub.empty:
        return {"period": label, "rows": []}
    agg = _model_agg(sub).sort_values("total", ascending=False).head(limit)
    total_all = int(sub["units_sold"].sum())
    rows = _to_json(agg)
    for i, r in enumerate(rows, 1):
        r["rank"] = i
        r["share"] = round(r["total"] / total_all * 100, 2) if total_all else 0
    return {"period": label, "total": total_all, "rows": rows}


def trend(model: str, make: str = None) -> dict:
    """某车型月销量趋势"""
    df = load_detail()
    m = df[df["model"] == model]
    if make:
        m = m[m["make"] == make]
    if m.empty:
        return {"model": model, "make": make, "points": []}
    g = m.groupby("ym")["units_sold"].sum().sort_index()
    return {
        "model": model,
        "make": m["make"].iloc[0],
        "is_ev": m["is_ev"].iloc[0],
        "points": [{"month": str(k.date())[:7], "sales": int(v)} for k, v in g.items()],
    }


def browse(page=1, page_size=15, make=None, price_min=None, price_max=None,
           energy="all", body="all", country="all", keyword="", sort="ym", order="desc") -> dict:
    """车型数据浏览：分页 + 多维筛选"""
    df = load_detail()
    m = df.copy()
    if make:
        m = m[m["make"] == make]
    if price_min is not None:
        m = m[m["price_wan"] >= price_min]
    if price_max is not None:
        m = m[m["price_wan"] <= price_max]
    if energy in ("EV", "Gasoline"):
        m = m[m["is_ev"] == energy]
    if body and body != "all":
        m = m[m["body_type"] == body]
    if country and country != "all":
        m = m[m["brand_country"] == country]
    if keyword:
        kw = keyword.strip()
        m = m[m["model"].astype(str).str.contains(kw, case=False, na=False)
              | m["make"].astype(str).str.contains(kw, case=False, na=False)]
    total = int(len(m))
    sort_col = "ym" if sort == "ym" else "units_sold"
    m = m.sort_values(sort_col, ascending=(order == "asc"))
    start = (page - 1) * page_size
    rows = m.iloc[start:start + page_size]
    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "rows": [
            {
                "model": safe(r["model"]),
                "make": safe(r["make"]),
                "units_sold": int(r["units_sold"]),
                "price_wan": round(float(r["price_wan"]), 1),
                "year_month": str(r["year_month"])[:7],
                "is_ev": safe(r["is_ev"]),
                "body_type": safe(r["body_type"]),
                "brand_country": safe(r["brand_country"]),
            }
            for _, r in rows.iterrows()
        ],
    }


def _to_json(agg: pd.DataFrame) -> list:
    out = []
    for _, r in agg.iterrows():
        out.append({
            "model": safe(r["model"]),
            "make": safe(r["make"]),
            "total": int(r["total"]),
            "avg_price": round(float(r["avg_price"]), 1),
            "min_price": round(float(r["min_price"]), 1),
            "max_price": round(float(r["max_price"]), 1),
            "brand_country": safe(r["brand_country"]),
            "country_label": COUNTRY_LABELS.get(safe(r["brand_country"]), safe(r["brand_country"])),
            "is_ev": safe(r["is_ev"]),
            "body_type": safe(r["body_type"]),
            "body_label": BODY_LABELS.get(safe(r["body_type"]), safe(r["body_type"])),
            "months": int(r["months"]),
            "last_ym": str(r["last_ym"].date())[:7] if hasattr(r["last_ym"], "date") else str(r["last_ym"])[:7],
            "last_sold": int(r["last_sold"]),
        })
    return out
