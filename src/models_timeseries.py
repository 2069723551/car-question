# ============================================================
# 文件路径：src/models_timeseries.py
# 功能：时间序列预测模型
#   - 季节分解 seasonal_decompose
#   - SARIMA 季节性自回归移动平均模型
#   - 按时间顺序划分训练/测试集，评估 MAE / RMSE / R²
#   - 支持对未来 N 个月进行外推预测
# ============================================================

import warnings

import numpy as np
import pandas as pd
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from statsmodels.tsa.seasonal import seasonal_decompose
from statsmodels.tsa.statespace.sarimax import SARIMAX

warnings.filterwarnings("ignore")


def decompose_series(series, period=12, model="multiplicative"):
    """对时间序列进行季节性分解。

    period : 季节周期（月度数据默认12）
    model  : additive(加法) / multiplicative(乘法)
    """
    return seasonal_decompose(series, model=model, period=period)


def fit_holt_winters(series, period=12, seasonal="add"):
    """训练 Holt-Winters 指数平滑模型（含趋势与季节性）。"""
    model = ExponentialSmoothing(
        series, trend="add", seasonal=seasonal, seasonal_periods=period,
        initialization_method="estimated"
    )
    fitted = model.fit(optimized=True)
    return fitted


def walk_forward_evaluate(series, period=12, test_ratio=0.2):
    """使用滚动预测（walk-forward）评估 Holt-Winters 模型。

    返回 (指标dict, 训练集, 测试集, 预测值Series)
    """
    n = len(series)
    n_test = int(np.ceil(n * test_ratio))
    train = series.iloc[:-n_test]
    test = series.iloc[-n_test:]

    model = ExponentialSmoothing(
        train, trend="add", seasonal="add", seasonal_periods=period,
        initialization_method="estimated"
    ).fit(optimized=True)
    pred = model.forecast(len(test))
    pred.index = test.index

    mae = float(np.mean(np.abs(test.values - pred.values)))
    rmse = float(np.sqrt(np.mean((test.values - pred.values) ** 2)))
    ss_res = float(np.sum((test.values - pred.values) ** 2))
    ss_tot = float(np.sum((test.values - np.mean(test.values)) ** 2))
    r2 = 1 - ss_res / ss_tot if ss_tot > 0 else 0.0

    metrics = {"MAE": round(mae, 2), "RMSE": round(rmse, 2), "R2": round(r2, 4)}
    return metrics, train, test, pred


def fit_sarima(series, order=(1, 1, 1), seasonal_order=(1, 1, 1, 12)):
    """拟合 SARIMA 季节性差分自回归移动平均模型。

    order           : (p, d, q) 非季节性阶数
    seasonal_order  : (P, D, Q, s) 季节性阶数，s 为季节周期
    """
    model = SARIMAX(
        series, order=order, seasonal_order=seasonal_order,
        enforce_stationarity=False, enforce_invertibility=False,
        simple_differencing=False,
    )
    fitted = model.fit(disp=False, maxiter=100)
    return fitted


def walk_forward_evaluate_sarima(series, test_ratio=0.2,
                                 order=(1, 1, 1), seasonal_order=(1, 1, 1, 12)):
    """使用 SARIMA 对测试集做多步动态预测并评估。

    返回 (指标dict, 训练集, 测试集, 预测值Series)
    """
    n = len(series)
    n_test = int(np.ceil(n * test_ratio))
    train = series.iloc[:-n_test]
    test = series.iloc[-n_test:]

    fitted = fit_sarima(train, order=order, seasonal_order=seasonal_order)
    pred = fitted.forecast(len(test))
    pred.index = test.index

    mae = float(np.mean(np.abs(test.values - pred.values)))
    rmse = float(np.sqrt(np.mean((test.values - pred.values) ** 2)))
    ss_res = float(np.sum((test.values - pred.values) ** 2))
    ss_tot = float(np.sum((test.values - np.mean(test.values)) ** 2))
    r2 = 1 - ss_res / ss_tot if ss_tot > 0 else 0.0

    metrics = {"MAE": round(mae, 2), "RMSE": round(rmse, 2), "R2": round(r2, 4)}
    return metrics, train, test, pred, fitted


def forecast_future(series, steps=12, period=12, model_name="hw"):
    """基于全量序列训练模型并对未来 steps 个月做预测。

    model_name : "hw" 使用 Holt-Winters；"sarima" 使用 SARIMA
    返回 (模型, 未来预测Series)
    """
    if model_name == "sarima":
        model = fit_sarima(series, order=(1, 1, 1), seasonal_order=(1, 1, 1, 12))
        fc = model.forecast(steps)
    else:
        model = ExponentialSmoothing(
            series, trend="add", seasonal="add", seasonal_periods=period,
            initialization_method="estimated"
        ).fit(optimized=True)
        fc = model.forecast(steps)
    future_index = pd.date_range(
        start=series.index[-1] + pd.DateOffset(months=1), periods=steps, freq="MS"
    )
    fc.index = future_index
    return model, fc


if __name__ == "__main__":
    from data_loader import load_monthly_car_sales

    s = load_monthly_car_sales()["sales"]
    metrics, train, test, pred = walk_forward_evaluate(s)
    print("[Holt-Winters] 测试集指标:", metrics)
    model, fc = forecast_future(s, steps=12)
    print("[未来12个月预测]")
    print(fc)
