# ============================================================
# 文件路径：src/visualize.py
# 功能：可视化模块
#   - 销量时序趋势图
#   - 季节性分解图
#   - 特征相关性热力图
#   - 回归模型预测对比图
#   - 时间序列模型预测 + 未来外推图
# 所有图片输出到 output/figures/ 目录
# ============================================================

from pathlib import Path

import matplotlib
matplotlib.use("Agg")  # 无界面后端，便于批量出图
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

from models_timeseries import decompose_series

# 中文字体配置（Windows 常见中文字体）
plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "Arial Unicode MS"]
plt.rcParams["axes.unicode_minus"] = False

OUTPUT_DIR = Path(__file__).resolve().parent.parent / "car-sales-backend" / "output" / "figures"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def savefig(fig, name):
    path = OUTPUT_DIR / name
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return path


def plot_series(series, title="月度汽车销量趋势", ylabel="销量(辆)", name="01_series_trend.png"):
    """绘制原始销量时序图。"""
    fig, ax = plt.subplots(figsize=(12, 4.5))
    ax.plot(series.index, series.values, color="#2c6fbb", linewidth=1.5)
    ax.set_title(title, fontsize=14)
    ax.set_ylabel(ylabel)
    ax.grid(alpha=0.3)
    fig.tight_layout()
    return savefig(fig, name)


def plot_multi_series(df, name="01b_mva_multi_series.png"):
    """绘制 MVA 数据集多序列对比（新车/二手车登记数）。"""
    fig, ax = plt.subplots(figsize=(12, 4.5))
    ax.plot(df.index, df["New"], label="新车登记数 (New)", color="#2c6fbb", linewidth=1.3)
    ax.plot(df.index, df["Used"], label="二手车登记数 (Used)", color="#d9822b", linewidth=1.3)
    ax.set_title("中国新能源(EV) vs 燃油车月度销量 (2018-2024)", fontsize=14)
    ax.set_ylabel("销量(辆)")
    ax.legend()
    ax.grid(alpha=0.3)
    fig.tight_layout()
    return savefig(fig, name)


def plot_decomposition(series, period=12, name="02_seasonal_decompose.png"):
    """绘制时间序列季节分解图（趋势/季节/残差）。"""
    result = decompose_series(series, period=period, model="multiplicative")
    fig, axes = plt.subplots(4, 1, figsize=(12, 10), sharex=True)
    axes[0].plot(result.observed, color="#333333")
    axes[0].set_title("原始序列 (Observed)")
    axes[1].plot(result.trend, color="#2c6fbb")
    axes[1].set_title("趋势 (Trend)")
    axes[2].plot(result.seasonal, color="#d9822b")
    axes[2].set_title("季节成分 (Seasonal)")
    axes[3].plot(result.resid, color="#7a7a7a")
    axes[3].set_title("残差 (Residual)")
    for ax in axes:
        ax.grid(alpha=0.3)
    fig.tight_layout()
    return savefig(fig, name)


def plot_correlation(feature_df, name="03_feature_correlation.png"):
    """绘制特征相关性热力图。"""
    import matplotlib.pyplot as plt
    corr = feature_df.corr()
    fig, ax = plt.subplots(figsize=(11, 9))
    im = ax.imshow(corr.values, cmap="RdBu_r", vmin=-1, vmax=1)
    ax.set_xticks(range(len(corr.columns)))
    ax.set_yticks(range(len(corr.columns)))
    ax.set_xticklabels(corr.columns, rotation=90, fontsize=8)
    ax.set_yticklabels(corr.columns, fontsize=8)
    for i in range(len(corr.columns)):
        for j in range(len(corr.columns)):
            ax.text(j, i, f"{corr.iloc[i, j]:.2f}", ha="center", va="center",
                    fontsize=6, color="white" if abs(corr.iloc[i, j]) > 0.6 else "black")
    fig.colorbar(im, ax=ax, shrink=0.8)
    fig.tight_layout()
    return savefig(fig, name)


def plot_regression_prediction(y_true, y_pred, train_end_date, title,
                               name="04_regression_prediction.png"):
    """绘制回归模型在测试集上的预测 vs 真实对比图。"""
    fig, ax = plt.subplots(figsize=(12, 4.5))
    ax.plot(y_true.index, y_true.values, label="真实销量", color="#2c6fbb", linewidth=1.6)
    ax.plot(y_pred.index, y_pred.values, label="预测销量", color="#e15759", linewidth=1.4, linestyle="--")
    ax.axvline(train_end_date, color="#7a7a7a", linestyle=":", alpha=0.7)
    ax.text(train_end_date, ax.get_ylim()[1] * 0.92, "训练/测试分界", color="#7a7a7a", fontsize=9)
    ax.set_title(title, fontsize=13)
    ax.set_ylabel("销量(辆)")
    ax.legend()
    ax.grid(alpha=0.3)
    fig.tight_layout()
    return savefig(fig, name)


def plot_timeseries_forecast(series, train, test, pred, future=None,
                             name="05_timeseries_forecast.png"):
    """绘制时间序列模型训练/测试/预测/未来外推对比图。"""
    fig, ax = plt.subplots(figsize=(13, 5))
    ax.plot(series.index, series.values, label="历史销量", color="#7f7f7f", linewidth=1.0, alpha=0.6)
    ax.plot(train.index, train.values, label="训练集", color="#2c6fbb", linewidth=1.4)
    ax.plot(test.index, test.values, label="测试集真实", color="#2ca02c", linewidth=1.6)
    ax.plot(pred.index, pred.values, label="测试集预测", color="#e15759", linewidth=1.4, linestyle="--")
    if future is not None:
        ax.plot(future.index, future.values, label="未来12个月预测", color="#d9822b",
                linewidth=1.8, linestyle="-.")
        ax.fill_between(future.index, future.values * 0.85, future.values * 1.15,
                        color="#d9822b", alpha=0.12)
    ax.set_title("时间序列模型销量预测", fontsize=13)
    ax.set_ylabel("销量(辆)")
    ax.legend(ncol=2, fontsize=9)
    ax.grid(alpha=0.3)
    fig.tight_layout()
    return savefig(fig, name)
