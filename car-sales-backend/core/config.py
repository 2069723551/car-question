import os
import pathlib

BASE_DIR = pathlib.Path(__file__).resolve().parent.parent
FRONTEND_DIR = pathlib.Path(
    os.getenv("FRONTEND_DIR", str(BASE_DIR.parent / "car-sales-web" / "dist"))
)
DATABASE_URL = f"sqlite:///{BASE_DIR / 'car_sales.db'}"
DATA_DIR = BASE_DIR / "data"
PREDICTIONS_DIR = BASE_DIR / "output" / "predictions"
FIGURES_DIR = BASE_DIR / "output" / "figures"
MAIN_CSV = "china_monthly.csv"
MVA_CSV = "china_car_sales.csv"
METRICS_JSON = "metrics.json"
FORECAST_CSV = "future_12m_predictions.csv"
REGRESSION_CSV = "regression_predictions.csv"
FIGURE_FILES = [
    "01_series_trend.png",
    "01b_mva_multi_series.png",
    "02_seasonal_decompose.png",
    "03_feature_correlation.png",
    "04_regression_prediction.png",
    "05_timeseries_forecast.png",
]