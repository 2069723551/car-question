# ============================================================
# 文件路径：car-sales-backend/crud/sales.py
# 作用：封装对三张表的所有数据库操作（CRUD）
#   SQL 操作全部由 ORM 框架映射为方法，无需手写 SQL
# ============================================================

from sqlalchemy.orm import Session

from models.sales import SalesRecord, PredictionRecord, QueryLog


# ============ 销量数据表 ============

def get_sales(db: Session, skip: int = 0, limit: int = 1000):
    """查询月度销量数据（支持分页）"""
    return db.query(SalesRecord).order_by(SalesRecord.date).offset(skip).limit(limit).all()


def get_sales_count(db: Session) -> int:
    """销量数据总条数"""
    return db.query(SalesRecord).count()


def create_sales_record(db: Session, date: str, sales: int) -> SalesRecord:
    """新增一条销量记录（导入时使用）"""
    record = SalesRecord(date=date, sales=sales)
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def sales_exists(db: Session) -> bool:
    """判断销量表是否已有数据（避免重复导入）"""
    return db.query(SalesRecord).count() > 0


# ============ 预测结果表 ============

def get_predictions(db: Session, skip: int = 0, limit: int = 100):
    """查询未来预测结果"""
    return db.query(PredictionRecord).order_by(PredictionRecord.date).offset(skip).limit(limit).all()


def get_predictions_count(db: Session) -> int:
    """预测结果总条数"""
    return db.query(PredictionRecord).count()


def create_prediction_record(db: Session, date: str, forecast: float) -> PredictionRecord:
    """新增一条预测记录（导入时使用）"""
    record = PredictionRecord(date=date, forecast=forecast)
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def predictions_exists(db: Session) -> bool:
    """判断预测表是否已有数据"""
    return db.query(PredictionRecord).count() > 0


# ============ 查询日志表 ============

def add_query_log(db: Session, endpoint: str, method: str = "GET", status: str = "success"):
    """记录一次接口查询"""
    log = QueryLog(endpoint=endpoint, method=method, status=status)
    db.add(log)
    db.commit()
    db.refresh(log)
    return log


def get_query_logs(db: Session, limit: int = 30):
    """查询最近调用日志（按时间倒序）"""
    return (
        db.query(QueryLog)
        .order_by(QueryLog.id.desc())
        .limit(limit)
        .all()
    )


def get_query_logs_count(db: Session) -> int:
    """日志总条数"""
    return db.query(QueryLog).count()


def get_db_stats(db: Session) -> dict:
    """数据库状态汇总（三张表记录数）"""
    return {
        "sales_records": get_sales_count(db),
        "prediction_records": get_predictions_count(db),
        "query_logs": get_query_logs_count(db),
    }
