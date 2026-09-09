# ============================================================
# 文件路径：car-sales-backend/routers/news.py
# 作用：汽车资讯接口
#   GET /api/news        获取最新汽车资讯列表（首页顶部展示）
#   GET /api/news/{id}   获取单条资讯全文（资讯详情页）
# ============================================================

from fastapi import APIRouter, HTTPException, Query
from services import news_service

router = APIRouter(prefix="/api/news", tags=["汽车资讯"])


@router.get("")
def get_news(limit: int = Query(6, ge=1, le=10)):
    """获取最新汽车资讯列表"""
    return {"success": True, "news": news_service.get_news(limit)}


@router.get("/{news_id}")
def get_news_detail(news_id: int):
    """获取单条资讯全文"""
    item = news_service.get_news_detail(news_id)
    if item is None:
        raise HTTPException(status_code=404, detail="资讯不存在")
    return {"success": True, "news": item}
