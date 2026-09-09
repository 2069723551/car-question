# ============================================================
# 文件路径：src/models_regression.py
# 功能：回归类销量预测模型
#   基于特征工程后的监督特征，训练：
#   - 线性回归 LinearRegression
#   - 随机森林回归 RandomForestRegressor
#   使用时间顺序划分训练/测试集（避免未来信息泄露），
#   评估指标：MAE / RMSE / R²
# ============================================================

import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score


def split_train_test(X, y, test_ratio=0.2):
    """按时间顺序划分训练集与测试集（不打乱）。"""
    n = len(y)
    n_test = int(np.ceil(n * test_ratio))
    n_train = n - n_test
    X_train, X_test = X.iloc[:n_train], X.iloc[n_train:]
    y_train, y_test = y.iloc[:n_train], y.iloc[n_train:]
    return X_train, X_test, y_train, y_test


def evaluate(y_true, y_pred):
    """计算回归评估指标。"""
    mae = mean_absolute_error(y_true, y_pred)
    rmse = float(np.sqrt(mean_squared_error(y_true, y_pred)))
    r2 = r2_score(y_true, y_pred)
    return {"MAE": round(mae, 2), "RMSE": round(rmse, 2), "R2": round(r2, 4)}


def train_linear_regression(X_train, y_train):
    """训练线性回归模型。"""
    model = LinearRegression()
    model.fit(X_train, y_train)
    return model


def train_random_forest(X_train, y_train, n_estimators=200, random_state=42):
    """训练随机森林回归模型。"""
    model = RandomForestRegressor(
        n_estimators=n_estimators, random_state=random_state, n_jobs=-1
    )
    model.fit(X_train, y_train)
    return model


def feature_importance(model, feature_names, top=10):
    """输出模型特征重要性（随机森林等树模型）。"""
    if hasattr(model, "feature_importances_"):
        imp = pd.Series(model.feature_importances_, index=feature_names)
        return imp.sort_values(ascending=False).head(top)
    return None


if __name__ == "__main__":
    from data_loader import load_monthly_car_sales
    from feature_engineer import build_supervised_features

    s = load_monthly_car_sales()["sales"]
    data = build_supervised_features(s)
    X = data.drop(columns=["y"])
    y = data["y"]

    X_train, X_test, y_train, y_test = split_train_test(X, y)
    for name, model in [
        ("LinearRegression", train_linear_regression(X_train, y_train)),
        ("RandomForest", train_random_forest(X_train, y_train)),
    ]:
        y_pred = model.predict(X_test)
        print(f"[{name}] 测试集指标:", evaluate(y_test, y_pred))
