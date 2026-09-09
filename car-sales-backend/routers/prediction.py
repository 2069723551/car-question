# ============================================================
# 文件路径：car-sales-backend/routers/prediction.py
# 说明：智能预测与推荐系统 API 路由
# ============================================================

from fastapi import APIRouter
from pydantic import BaseModel, Field
from typing import Optional
from services.prediction_service import recommendation_engine

router = APIRouter(prefix="/api/prediction", tags=["智能预测与推荐"])


class PredictionRequest(BaseModel):
    """预测请求参数"""
    month: int = Field(default=1, ge=1, le=12, description="月份 (1-12)")
    price: float = Field(default=15.0, gt=0, description="价格 (万元)")
    promotion: float = Field(default=5.0, ge=0, le=10, description="促销力度 (0-10)")
    economy_index: float = Field(default=70.0, ge=0, le=100, description="经济指数 (0-100)")
    competitor_price: float = Field(default=16.0, gt=0, description="竞争对手价格 (万元)")


@router.post("/predict")
def predict_sales(request: PredictionRequest):
    """
    预测销量

    参数说明：
    - month: 预测月份 (1-12)
    - price: 产品价格（万元）
    - promotion: 促销力度 (0-10，0表示无促销，10表示最大力度)
    - economy_index: 经济指数 (0-100，反映整体经济环境)
    - competitor_price: 竞争对手价格（万元）
    """
    params = request.dict()
    result = recommendation_engine.prediction_engine.predict(params)
    return {
        "success": True,
        "data": result,
        "input_params": params
    }


@router.post("/recommend")
def get_recommendations(request: PredictionRequest):
    """
    获取营销推荐

    基于当前市场参数，提供：
    - 销量预测
    - 价格策略建议
    - 促销活动建议
    - 最优策略组合
    - 风险评估
    """
    params = request.dict()
    result = recommendation_engine.generate_recommendations(params)
    return {
        "success": True,
        "data": result,
        "input_params": params
    }


@router.get("/demo")
def get_demo_scenarios():
    """
    获取演示场景

    提供几个预设场景供用户快速体验
    """
    scenarios = [
        {
            "name": "旺季高价策略",
            "description": "销售旺季，价格较高，适度促销",
            "params": {
                "month": 5,
                "price": 17.5,
                "promotion": 5.0,
                "economy_index": 75.0,
                "competitor_price": 16.0
            }
        },
        {
            "name": "淡季促销策略",
            "description": "销售淡季，降价促销争取市场份额",
            "params": {
                "month": 1,
                "price": 14.0,
                "promotion": 8.0,
                "economy_index": 65.0,
                "competitor_price": 16.0
            }
        },
        {
            "name": "经济低迷应对",
            "description": "经济下行，竞争激烈，需要谨慎定价",
            "params": {
                "month": 3,
                "price": 15.5,
                "promotion": 7.0,
                "economy_index": 55.0,
                "competitor_price": 15.0
            }
        },
        {
            "name": "竞争优势策略",
            "description": "价格优势明显，经济环境良好",
            "params": {
                "month": 4,
                "price": 14.5,
                "promotion": 6.0,
                "economy_index": 80.0,
                "competitor_price": 17.0
            }
        }
    ]

    return {
        "success": True,
        "data": scenarios
    }


@router.get("/factors")
def get_prediction_factors():
    """
    获取预测因子说明

    返回模型使用的各个因子及其影响说明
    """
    factors = {
        "month": {
            "name": "月份",
            "type": "integer",
            "range": "1-12",
            "description": "销售月份，不同月份有明显的季节性差异",
            "impact": "旺季（3-6月）销量提升20-30%，淡季（1-2、7-9月）销量下降15-25%"
        },
        "price": {
            "name": "价格",
            "type": "float",
            "range": ">0",
            "unit": "万元",
            "description": "产品定价",
            "impact": "价格每上涨10%，预计销量下降约1.5%"
        },
        "promotion": {
            "name": "促销力度",
            "type": "float",
            "range": "0-10",
            "description": "促销活动力度，0表示无促销，10表示最大力度促销",
            "impact": "促销力度每增加1个单位，预计销量提升约2.5%"
        },
        "economy_index": {
            "name": "经济指数",
            "type": "float",
            "range": "0-100",
            "description": "宏观经济环境指标，反映消费者购买力和市场信心",
            "impact": "经济指数每提升10个点，预计销量提升约3%"
        },
        "competitor_price": {
            "name": "竞争对手价格",
            "type": "float",
            "range": ">0",
            "unit": "万元",
            "description": "主要竞品的价格",
            "impact": "竞品价格高于自身价格时，每高出10%，预计销量提升约1%"
        }
    }

    return {
        "success": True,
        "data": factors
    }
