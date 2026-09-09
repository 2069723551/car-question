# ============================================================
# 文件路径：car-sales-backend/services/forecast_service.py
# 说明：读取已训练的模型指标与未来预测结果
# ============================================================

import json
import pandas as pd

from core.config import PREDICTIONS_DIR, METRICS_JSON, FORECAST_CSV, REGRESSION_CSV, FIGURE_FILES, FIGURES_DIR


def _load_csv(filename: str) -> pd.DataFrame:
    """读取 CSV 并清洗列名（去空格）"""
    path = PREDICTIONS_DIR / filename
    df = pd.read_csv(path)
    df.columns = [str(c).strip() for c in df.columns]
    return df


def get_metrics() -> dict:
    """四类模型评估指标（已训练结果）"""
    path = PREDICTIONS_DIR / METRICS_JSON
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data


def get_forecast() -> list:
    """未来 12 个月预测：[{date, forecast}]"""
    df = _load_csv(FORECAST_CSV)
    # 第一列为日期（索引列可能被命名为 Unnamed: 0）
    date_col = df.columns[0]
    val_col = df.columns[1]
    return [
        {"date": str(row[date_col]), "forecast": round(float(row[val_col]), 2)}
        for _, row in df.iterrows()
    ]


def get_regression_predictions() -> list:
    """回归模型测试集预测：[{date, actual, pred_rf, pred_lr}]"""
    df = _load_csv(REGRESSION_CSV)
    date_col = [c for c in df.columns if "date" in c.lower() or "month" in c.lower()][0]
    others = [c for c in df.columns if c != date_col]
    return [
        {
            "date": str(row[date_col]),
            **{c: (round(float(row[c]), 2) if pd.notna(row[c]) else None) for c in others},
        }
        for _, row in df.iterrows()
    ]


def get_figure_list() -> list:
    """图表文件列表（output/figures 下）"""
    figures = []
    for name in FIGURE_FILES:
        p = FIGURES_DIR / name
        if p.exists():
            figures.append({
                "name": name,
                "url": f"/figures/{name}",
            })
    return figures
