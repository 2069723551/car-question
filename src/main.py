# ============================================================
# 文件路径：src/main.py
# 功能：汽车销量预测系统 —— 主流程入口
#   步骤：
#     1) 数据加载与清洗（中国乘用车月度总销量 + 车型明细多维度数据）
#     2) 探索性分析与季节分解
#     3) 特征工程（监督特征构造）
#     4) 回归模型训练与评估（线性回归 / 随机森林）
#     5) 时间序列模型训练与评估（Holt-Winters / SARIMA）
#     6) 未来销量预测
#     7) 可视化与指标输出
#   运行：python main.py
# ============================================================

import json
import sys
from pathlib import Path

import pandas as pd

# 保证可以 import 同目录模块
sys.path.insert(0, str(Path(__file__).resolve().parent))

from data_loader import load_monthly_car_sales, load_mva_sales
from feature_engineer import build_supervised_features
from models_regression import (
    split_train_test, evaluate,
    train_linear_regression, train_random_forest, feature_importance,
)
from models_timeseries import (
    walk_forward_evaluate, walk_forward_evaluate_sarima,
    forecast_future,
)
import visualize as viz

PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_PRED = PROJECT_ROOT / "car-sales-backend" / "output" / "predictions"
OUTPUT_PRED.mkdir(parents=True, exist_ok=True)


def run_pipeline():
    results = {}

    # ---------------- 1. 数据加载 ----------------
    print("=" * 60)
    print("[1] 数据加载与清洗")
    mcs = load_monthly_car_sales()
    mva = load_mva_sales()
    print(f"    - 中国乘用车月度总销量: {mcs.shape[0]} 条记录 "
          f"({mcs.index.min().date()} ~ {mcs.index.max().date()})")
    print(f"    - 新能源/燃油月度聚合: {mva.shape[0]} 条记录 "
          f"({mva.index.min().date()} ~ {mva.index.max().date()})")

    # 主预测序列：中国乘用车月度总销量（季节性强，预测效果好）
    series = mcs["sales"]
    results["data_source"] = "china_monthly.csv（中国乘用车月度总销量，乘联会 CPCA 来源）"
    results["data_range"] = [str(series.index.min().date()), str(series.index.max().date())]
    results["data_count"] = int(len(series))

    # ---------------- 2. 探索性分析与季节分解 ----------------
    print("[2] 探索性分析与季节分解")
    viz.plot_series(series, title="中国乘用车月度销量趋势 (2018-2024)",
                    ylabel="销量(辆)", name="01_series_trend.png")
    viz.plot_decomposition(series, period=12, name="02_seasonal_decompose.png")
    # MVA 多维度数据对比展示（新车/二手车登记量）
    viz.plot_multi_series(mva, name="01b_mva_multi_series.png")
    results["desc_stats"] = {
        "mean": round(float(series.mean()), 2),
        "std": round(float(series.std()), 2),
        "min": float(series.min()),
        "max": float(series.max()),
    }
    print(f"    均值={results['desc_stats']['mean']}, "
          f"最大值={results['desc_stats']['max']}")

    # ---------------- 3. 特征工程 ----------------
    print("[3] 特征工程")
    data = build_supervised_features(series)
    X = data.drop(columns=["y"])
    y = data["y"]
    viz.plot_correlation(data, name="03_feature_correlation.png")
    results["feature_count"] = X.shape[1]
    results["feature_names"] = list(X.columns)
    print(f"    构造特征 {X.shape[1]} 个, 有效样本 {X.shape[0]} 条")

    # ---------------- 4. 回归模型 ----------------
    print("[4] 回归模型训练与评估")
    X_train, X_test, y_train, y_test = split_train_test(X, y, test_ratio=0.2)
    train_end_date = y_train.index[-1]

    model_lr = train_linear_regression(X_train, y_train)
    pred_lr = pd.Series(model_lr.predict(X_test), index=y_test.index)
    metrics_lr = evaluate(y_test, pred_lr)
    results["regression"] = {"linear_regression": metrics_lr}
    print(f"    线性回归: {metrics_lr}")

    model_rf = train_random_forest(X_train, y_train)
    pred_rf = pd.Series(model_rf.predict(X_test), index=y_test.index)
    metrics_rf = evaluate(y_test, pred_rf)
    results["regression"]["random_forest"] = metrics_rf
    print(f"    随机森林: {metrics_rf}")

    # 随机森林特征重要性
    imp = feature_importance(model_rf, X.columns)
    results["feature_importance"] = (imp.to_dict() if imp is not None else None)

    # 回归预测对比图（随机森林效果更好，以其作图）
    viz.plot_regression_prediction(
        y_test, pred_rf, train_end_date,
        title="随机森林回归模型预测 vs 真实 (测试集)",
        name="04_regression_prediction.png",
    )

    # 保存回归预测结果
    reg_pred_df = pd.DataFrame({"actual": y_test, "pred_rf": pred_rf, "pred_lr": pred_lr})
    reg_pred_df.to_csv(OUTPUT_PRED / "regression_predictions.csv", encoding="utf-8-sig")
    print(f"    回归预测结果已保存: {OUTPUT_PRED / 'regression_predictions.csv'}")

    # ---------------- 5. 时间序列模型 ----------------
    print("[5] 时间序列模型训练与评估")
    hw_metrics, train, test, pred = walk_forward_evaluate(series, period=12, test_ratio=0.2)
    print(f"    Holt-Winters: {hw_metrics}")

    try:
        sarima_metrics, _, _, sarima_pred, _ = walk_forward_evaluate_sarima(
            series, test_ratio=0.2)
        print(f"    SARIMA: {sarima_metrics}")
        results["timeseries"] = {"holt_winters": hw_metrics, "sarima": sarima_metrics}
        if sarima_metrics["R2"] >= hw_metrics["R2"]:
            ts_metrics = sarima_metrics
            ts_pred = sarima_pred
        else:
            ts_metrics = hw_metrics
            ts_pred = pred
    except Exception as e:
        print(f"    [警告] SARIMA 训练失败，使用 Holt-Winters 结果: {e}")
        results["timeseries"] = {"holt_winters": hw_metrics}
        ts_metrics = hw_metrics
        ts_pred = pred

    # ---------------- 6. 未来预测 ----------------
    print("[6] 未来12个月销量预测")
    _, future = forecast_future(series, steps=12, period=12, model_name="sarima")
    viz.plot_timeseries_forecast(series, train, test, ts_pred, future,
                                 name="05_timeseries_forecast.png")
    future.to_csv(OUTPUT_PRED / "future_12m_predictions.csv", encoding="utf-8-sig")
    results["future_prediction"] = {str(k.date()): round(float(v), 2) for k, v in future.items()}
    print("    未来12个月预测:")
    for k, v in results["future_prediction"].items():
        print(f"      {k}: {v}")

    # ---------------- 7. 指标汇总输出 ----------------
    results["model_comparison"] = {
        "linear_regression": metrics_lr,
        "random_forest": metrics_rf,
        "holt_winters": hw_metrics,
        "sarima": results["timeseries"].get("sarima", ts_metrics),
    }
    with open(OUTPUT_PRED / "metrics.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2, default=str)
    print(f"\n全部指标与结果已保存: {OUTPUT_PRED / 'metrics.json'}")
    print("=" * 60)
    return results


if __name__ == "__main__":
    run_pipeline()
