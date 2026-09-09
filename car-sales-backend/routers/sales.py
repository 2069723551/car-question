# ============================================================
# 文件路径：car-sales-backend/routers/sales.py
# 说明：汽车销量预测系统 API 路由
#   数据类接口已改为从 SQLite 数据库读取，每次调用自动记录查询日志
# ============================================================

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from services import data_service, forecast_service
from crud import sales as crud_sales
from schemas.sales import SalesRecordResponse, PredictionRecordResponse, QueryLogResponse, DbStatsResponse
from core.database import get_db

router = APIRouter(prefix="/api", tags=["汽车销量预测"])


def _log(db: Session, endpoint: str):
    """记录一次接口查询日志"""
    try:
        crud_sales.add_query_log(db, endpoint=endpoint, method="GET", status="success")
    except Exception:
        pass


@router.get("/overview")
def get_overview(db: Session = Depends(get_db)):
    """数据集概览：记录数、时间范围、统计量"""
    _log(db, "/api/overview")
    return data_service.get_overview()


@router.get("/series", response_model=list[SalesRecordResponse])
def get_series(db: Session = Depends(get_db)):
    """主数据集月度销量序列（从数据库 sales_records 表读取）"""
    _log(db, "/api/series")
    return crud_sales.get_sales(db, limit=2000)


@router.get("/multi-series")
def get_multi_series(db: Session = Depends(get_db)):
    """辅助数据集新车/二手车登记序列"""
    _log(db, "/api/multi-series")
    return data_service.get_mva_series_json()


@router.get("/metrics")
def get_metrics(db: Session = Depends(get_db)):
    """四类模型评估指标"""
    _log(db, "/api/metrics")
    return forecast_service.get_metrics()


@router.get("/forecast", response_model=list[PredictionRecordResponse])
def get_forecast(db: Session = Depends(get_db)):
    """未来 12 个月销量预测（从数据库 prediction_records 表读取）"""
    _log(db, "/api/forecast")
    return crud_sales.get_predictions(db, limit=100)


@router.get("/regression")
def get_regression(db: Session = Depends(get_db)):
    """回归模型测试集真实值 vs 预测值"""
    _log(db, "/api/regression")
    return forecast_service.get_regression_predictions()


@router.get("/figures")
def get_figures(db: Session = Depends(get_db)):
    """可视化图表文件列表"""
    _log(db, "/api/figures")
    return forecast_service.get_figure_list()


# ============ 数据库相关接口 ============

@router.get("/db-stats", response_model=DbStatsResponse)
def get_db_stats(db: Session = Depends(get_db)):
    """数据库状态：三张表记录数"""
    return crud_sales.get_db_stats(db)


@router.get("/logs", response_model=list[QueryLogResponse])
def get_logs(limit: int = 20, db: Session = Depends(get_db)):
    """最近接口查询日志（倒序）"""
    return crud_sales.get_query_logs(db, limit=limit)
