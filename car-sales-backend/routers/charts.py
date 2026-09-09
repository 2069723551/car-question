# ============================================================
# 文件路径：car-sales-backend/routers/charts.py
# 作用：数据图集接口（数据可视化大屏）
#   GET /api/charts/all   返回全部图表聚合数据
# ============================================================

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from services import charts_service
from core.database import get_db
from crud import sales as crud_sales

router = APIRouter(prefix="/api/charts", tags=["数据图集"])


@router.get("/all")
def get_all_charts(db: Session = Depends(get_db)):
    """返回数据图集全部数据（年度/季节/移动平均/同比/分布/新车二手等）"""
    try:
        crud_sales.add_query_log(db, endpoint="/api/charts/all", method="GET", status="success")
    except Exception:
        pass
    return {"success": True, "data": charts_service.get_chart_data()}
