# ============================================================
# 文件路径：car-sales-backend/routers/ranking.py
# 作用：品牌销量排行榜接口
#   GET /api/ranking/all —— 排行榜全部数据（榜单+趋势+占比）
# ============================================================

from fastapi import APIRouter

from services.ranking_service import get_ranking_data

router = APIRouter(prefix="/api/ranking", tags=["ranking"])


@router.get("/all")
def ranking_all():
    """返回排行榜聚合数据"""
    data = get_ranking_data()
    return {"code": 0, "data": data}
