# ============================================================
# 文件路径：car-sales-backend/core/database.py
# 说明：SQLite 数据库引擎与会话管理
#   每次需要使用到数据库增删查改时，只引入 get_db() 即可
# ============================================================

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

from core.config import DATABASE_URL

# 1. 创建数据库引擎（SQLite，check_same_thread=False 兼容 FastAPI 多线程）
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {},
)

# 2. 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 3. 创建声明基类
Base = declarative_base()

# 4. 依赖函数：获取数据库会话
def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
