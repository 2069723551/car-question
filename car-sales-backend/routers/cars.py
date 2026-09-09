# ============================================================
# 文件路径：car-sales-backend/routers/cars.py
# 说明：选车助手 / 车型排行 / 车型数据浏览 接口
# ============================================================

from fastapi import APIRouter, Query

from services import car_service

router = APIRouter(prefix="/api/cars", tags=["cars"])


@router.get("/meta")
def get_meta():
    """筛选项元数据（厂商列表 / 车身类型 / 价格范围 / 国别）"""
    return {"code": 0, "data": car_service.get_meta()}


@router.get("/recommend")
def recommend(
    budget_min: float = Query(None, ge=0),
    budget_max: float = Query(None, ge=0),
    energy: str = "all",
    body: str = "all",
    country: str = "all",
    limit: int = Query(12, ge=1, le=50),
):
    """选车推荐：预算/能源/车身/国别筛选，按累计销量热度排序"""
    return {"code": 0, "data": car_service.recommend(budget_min, budget_max, energy, body, country, limit)}


@router.get("/trend")
def trend(model: str, make: str = None):
    """车型月销量趋势"""
    return {"code": 0, "data": car_service.trend(model, make)}


@router.get("/top")
def top(period: str = "total", limit: int = Query(20, ge=1, le=100)):
    """车型销量 TOP 榜：period=total|latest|年份(如 2023)"""
    return {"code": 0, "data": car_service.top(period, limit)}


@router.get("/browse")
def browse(
    page: int = Query(1, ge=1),
    page_size: int = Query(15, ge=1, le=100),
    make: str = None,
    price_min: float = Query(None, ge=0),
    price_max: float = Query(None, ge=0),
    energy: str = "all",
    body: str = "all",
    country: str = "all",
    keyword: str = "",
    sort: str = "ym",
    order: str = "desc",
):
    """车型数据浏览：分页 + 多维筛选"""
    return {
        "code": 0,
        "data": car_service.browse(page, page_size, make, price_min, price_max,
                                   energy, body, country, keyword, sort, order),
    }
