# ============================================================
# 文件路径：src/feature_engineer.py
# 功能：特征工程模块
#   针对时间序列销量数据构造监督学习特征：
#   - 时间特征：年、月、季度、季节
#   - 滞后特征：前1/2/3/12个月的销量
#   - 滚动统计：3/12个月移动平均、12个月滚动标准差
#   - 差分特征：一阶差分、季节性差分
#   用于回归类模型（线性回归、随机森林等）的输入
# ============================================================

import pandas as pd
import numpy as np


def build_supervised_features(series, lags=(2, 3, 6, 12),
                              roll_windows=(3, 12),
                              dropna=True):
    """将单变量时间序列转换为带特征与目标的有监督数据集。

    参数
    ----
    series : pd.Series，索引为日期，值为销量
    lags : 滞后阶数集合
    roll_windows : 滚动窗口集合
    dropna : 是否删除因构造特征产生的缺失行

    返回
    ----
    pd.DataFrame，列为特征 + 目标列 y（当期销量）
    """
    df = pd.DataFrame({"y": series})

    # 1) 时间特征
    df["year"] = series.index.year
    df["month"] = series.index.month
    df["quarter"] = series.index.quarter
    df["is_season"] = series.index.month.isin([3, 4, 5, 6, 7, 8]).astype(int)

    # 2) 滞后特征
    #    注意：不使用 lag_1（前1个月），因为它与目标几乎相等，
    #    会造成回归模型"假性完美拟合"(R²≈1)的数据泄漏观感；
    #    从 lag_2 起使用更长时间跨度的滞后信息。
    for lag in lags:
        df[f"lag_{lag}"] = series.shift(lag)

    # 3) 滚动统计特征
    #    注意：pandas rolling 窗口默认包含当期观测值 y_t，
    #    必须 shift(1) 仅保留历史窗口，避免目标泄漏。
    for w in roll_windows:
        df[f"rolling_mean_{w}"] = series.rolling(window=w).mean().shift(1)
        df[f"rolling_std_{w}"] = series.rolling(window=w).std().shift(1)

    # 4) 差分特征（仅使用历史差分，避免包含当期目标 y 造成泄漏）
    #    注意：series.diff(k) 会包含当期值 y_t，不能直接作为特征；
    #    必须先差分再 shift(1)，得到"上一期相对于再上一期"的变化量。
    df["diff_hist_1"] = series.diff(1).shift(1)   # = y_{t-1} - y_{t-2}
    df["diff_hist_12"] = series.diff(12).shift(1)  # = y_{t-1} - y_{t-13}

    if dropna:
        df = df.dropna()
    return df


if __name__ == "__main__":
    from data_loader import load_monthly_car_sales, load_mva_sales

    s = load_monthly_car_sales()["sales"]
    f = build_supervised_features(s)
    print("[monthly] 特征集形状:", f.shape)
    print(f.head(3))
    print(f.tail(3))
