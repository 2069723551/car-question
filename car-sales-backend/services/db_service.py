# ============================================================
# 文件路径：car-sales-backend/services/db_service.py
# 说明：数据库初始化与数据导入
#   - 启动时建表
#   - 将 CSV 数据集与预测结果导入 SQLite（幂等：已有数据则跳过）
# ============================================================

import logging
import pandas as pd

from core.database import Base, engine, SessionLocal
from core.config import DATA_DIR, PREDICTIONS_DIR, MAIN_CSV, FORECAST_CSV
from crud import sales as crud_sales

logger = logging.getLogger(__name__)


def init_db():
    """创建数据库表"""
    Base.metadata.create_all(bind=engine)
    logger.info("数据库表初始化完成（sales_records / prediction_records / query_logs）")


def import_data():
    """导入数据到数据库（幂等）"""
    db = SessionLocal()
    try:
        # 1. 导入主数据集月度销量（中国乘用车月度总销量）
        if not crud_sales.sales_exists(db):
            path = DATA_DIR / MAIN_CSV
            df = pd.read_csv(path)
            df.columns = ["date", "sales"]
            df["date"] = pd.to_datetime(df["date"]).dt.strftime("%Y-%m-%d")
            for _, row in df.iterrows():
                crud_sales.create_sales_record(db, str(row["date"]), int(row["sales"]))
            logger.info(f"销量数据导入完成：{len(df)} 条（中国乘用车月度总销量 2018-2024）")
        else:
            logger.info("销量数据已存在，跳过导入")

        # 2. 导入未来预测结果
        if not crud_sales.predictions_exists(db):
            path = PREDICTIONS_DIR / FORECAST_CSV
            df = pd.read_csv(path)
            date_col = str(df.columns[0])
            val_col = str(df.columns[1])
            for _, row in df.iterrows():
                crud_sales.create_prediction_record(db, str(row[date_col])[:10], float(row[val_col]))
            logger.info(f"预测结果导入完成：{len(df)} 条")
        else:
            logger.info("预测结果已存在，跳过导入")
    finally:
        db.close()


def startup_init():
    """启动时统一初始化（建表 + 导入数据）"""
    init_db()
    import_data()
