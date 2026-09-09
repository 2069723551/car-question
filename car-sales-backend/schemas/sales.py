# ============================================================
# 文件路径：car-sales-backend/schemas/sales.py
# 作用：Pydantic 响应模型（支持 ORM 对象转换）
# ============================================================

from pydantic import BaseModel
from datetime import datetime


class SalesRecordResponse(BaseModel):
    """销量数据响应"""
    id: int
    date: str
    sales: int

    class Config:
        from_attributes = True  # 支持 ORM 对象转换


class PredictionRecordResponse(BaseModel):
    """预测结果响应"""
    id: int
    date: str
    forecast: float

    class Config:
        from_attributes = True


class QueryLogResponse(BaseModel):
    """查询日志响应"""
    id: int
    endpoint: str
    method: str
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


class DbStatsResponse(BaseModel):
    """数据库状态响应"""
    sales_records: int
    prediction_records: int
    query_logs: int
