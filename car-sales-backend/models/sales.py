# ============================================================
# 文件路径：car-sales-backend/models/sales.py
# 作用：定义数据库表结构（SQLAlchemy ORM）
#   三张表：
#   1. sales_records        月度销量数据表（从 CSV 导入，108 条）
#   2. prediction_records   未来 12 个月预测结果表（12 条）
#   3. query_logs           接口查询日志表（每次 API 调用自动记录）
# ============================================================

from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.sql import func

from core.database import Base


class SalesRecord(Base):
    """月度汽车销量数据表（主数据集）"""
    __tablename__ = "sales_records"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(String(10), unique=True, index=True, nullable=False)  # 日期 YYYY-MM-DD
    sales = Column(Integer, nullable=False)                             # 当月销量（辆）
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<SalesRecord(date={self.date}, sales={self.sales})>"


class PredictionRecord(Base):
    """未来 12 个月销量预测结果表"""
    __tablename__ = "prediction_records"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(String(10), unique=True, index=True, nullable=False)  # 预测月份
    forecast = Column(Float, nullable=False)                            # 预测销量
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<PredictionRecord(date={self.date}, forecast={self.forecast})>"


class QueryLog(Base):
    """接口查询日志表：记录每次前端请求"""
    __tablename__ = "query_logs"

    id = Column(Integer, primary_key=True, index=True)
    endpoint = Column(String(100), nullable=False)   # 请求路径，如 /api/series
    method = Column(String(10), nullable=False)      # 请求方法，如 GET
    status = Column(String(20), nullable=False)      # 结果状态，如 success / error
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<QueryLog(endpoint={self.endpoint}, status={self.status})>"
