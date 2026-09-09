# ============================================================
# 文件路径：src/data_loader.py
# 功能：数据加载与清洗模块（中国乘用车销量数据）
#   - load_monthly_car_sales()：加载中国乘用车月度总销量(2018-2024，76条)
#   - load_mva_sales()：加载中国乘用车车型-月度销量明细(38806条)
# 数据来源：
#   - china_monthly.csv：中国乘用车月度总销量（由 china_car_sales.csv 聚合，2018-01 至 2024-04）
#   - china_car_sales.csv：中国乘用车车型-月度销量（乘联会 CPCA 登记记录整理）
# ============================================================

from pathlib import Path

import pandas as pd

# 数据目录：项目根目录下的 data/
DATA_DIR = Path(__file__).resolve().parent.parent / "car-sales-backend" / "data"


def load_monthly_car_sales(path=None):
    """加载中国乘用车月度总销量（2018-01 至 2024-04，共76条记录）。

    该数据集为单变量时间序列，列为：Month(月份) / Sales(销量)。
    """
    path = Path(path) if path else DATA_DIR / "china_monthly.csv"
    df = pd.read_csv(path)
    df.columns = [c.strip() for c in df.columns]
    # 构造日期索引
    df["date"] = pd.to_datetime(df["Month"], format="%Y-%m")
    df = df.rename(columns={"Sales": "sales"}).set_index("date").sort_index()
    df["sales"] = pd.to_numeric(df["sales"], errors="coerce")
    df = df.dropna()
    df.index.name = "date"
    return df


def load_mva_sales(path=None):
    """加载中国乘用车销量并按月聚合新能源(EV)/燃油车销量（2018-01 至 2024-04）。

    返回列：New(新能源EV月销量) / Used(燃油车月销量)，索引为年月。
    原始明细列：model(车型) / make(厂商) / units_sold(月销量) / low_price(价格·千元)
        / year_month(年月) / is_ev(是否新能源) / body_type(车身类型) / brand(品牌)
        / brand_country(品牌国别)
    """
    path = Path(path) if path else DATA_DIR / "china_car_sales.csv"
    df = pd.read_csv(path)
    df.columns = [c.strip() for c in df.columns]
    df["date"] = pd.to_datetime(df["year_month"], errors="coerce")
    df["units_sold"] = pd.to_numeric(df["units_sold"], errors="coerce")
    df = df.dropna(subset=["date", "units_sold"])
    df["kind"] = df["is_ev"].map(lambda x: "EV" if x == "EV" else "fuel")
    piv = (
        df.pivot_table(index="date", columns="kind", values="units_sold", aggfunc="sum")
        .fillna(0)
        .reset_index()
        .set_index("date")
        .sort_index()
    )
    for col in ("EV", "fuel"):
        if col not in piv.columns:
            piv[col] = 0
    piv = piv.rename(columns={"EV": "New", "fuel": "Used"})
    piv.index.name = "date"
    return piv


if __name__ == "__main__":
    m = load_monthly_car_sales()
    print("[china_monthly] 形状:", m.shape)
    print(m.head())
    print(m.tail())
    print("=" * 50)
    v = load_mva_sales()
    print("[china_car_sales] 形状:", v.shape)
    print(v[["make", "model", "units_sold"]].head())
