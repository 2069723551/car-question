"""
智能预测与推荐服务
提供实时预测和营销推荐功能
"""
from typing import Dict, Any, List
import pandas as pd
from datetime import datetime, timedelta
import random

# 简化的预测模型（实际应该使用训练好的模型）
class SalesPredictionEngine:
    """销量预测引擎"""

    def __init__(self):
        # 基准销量（基于中国车市主流热销车型月均销量，约 3 万辆/月）
        self.base_sales = 30000

        # 季节性因子（1-12月，基于中国 2018-2024 实测月度销量计算：
        # 12 月年末冲量最高 1.26，2 月春节淡季最低 0.63）
        self.seasonal_factors = {
            1: 1.07, 2: 0.63, 3: 0.95, 4: 0.85,
            5: 0.92, 6: 1.00, 7: 0.94, 8: 1.00,
            9: 1.10, 10: 1.12, 11: 1.17, 12: 1.26
        }

        # 影响因子权重
        self.weights = {
            'price': -0.15,          # 价格负相关
            'promotion': 0.25,       # 促销正相关
            'economy_index': 0.30,   # 经济指数正相关
            'competitor_price': 0.10, # 竞争对手价格正相关
            'season': 1.0            # 季节因子
        }

    def predict(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        预测销量
        params:
            - month: 月份 (1-12)
            - price: 价格 (万元)
            - promotion: 促销力度 (0-10)
            - economy_index: 经济指数 (0-100)
            - competitor_price: 竞争对手价格 (万元)
        """
        month = params.get('month', datetime.now().month)
        price = params.get('price', 15.0)
        promotion = params.get('promotion', 5.0)
        economy_index = params.get('economy_index', 70.0)
        competitor_price = params.get('competitor_price', 16.0)

        # 基础销量
        predicted_sales = self.base_sales

        # 应用季节性因子
        seasonal_factor = self.seasonal_factors.get(month, 1.0)
        predicted_sales *= seasonal_factor

        # 应用价格影响
        price_effect = (price - 15.0) / 15.0  # 以15万为基准
        predicted_sales *= (1 + self.weights['price'] * price_effect)

        # 应用促销影响
        promotion_effect = (promotion - 5.0) / 5.0  # 以5为基准
        predicted_sales *= (1 + self.weights['promotion'] * promotion_effect)

        # 应用经济指数影响
        economy_effect = (economy_index - 70.0) / 70.0  # 以70为基准
        predicted_sales *= (1 + self.weights['economy_index'] * economy_effect)

        # 应用竞争对手价格影响
        competitor_effect = (competitor_price - price) / price
        predicted_sales *= (1 + self.weights['competitor_price'] * competitor_effect)

        # 计算置信区间 (±15%)
        confidence_lower = predicted_sales * 0.85
        confidence_upper = predicted_sales * 1.15

        return {
            'predicted_sales': int(predicted_sales),
            'confidence_interval': {
                'lower': int(confidence_lower),
                'upper': int(confidence_upper)
            },
            'factors_impact': {
                'seasonal': f"{(seasonal_factor - 1) * 100:.1f}%",
                'price': f"{price_effect * self.weights['price'] * 100:.1f}%",
                'promotion': f"{promotion_effect * self.weights['promotion'] * 100:.1f}%",
                'economy': f"{economy_effect * self.weights['economy_index'] * 100:.1f}%"
            }
        }


class RecommendationEngine:
    """营销推荐引擎"""

    def __init__(self):
        self.prediction_engine = SalesPredictionEngine()

    def generate_recommendations(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        基于预测结果生成营销推荐
        """
        # 当前预测
        current_prediction = self.prediction_engine.predict(params)
        current_sales = current_prediction['predicted_sales']

        recommendations = []

        # 1. 价格优化建议
        price_rec = self._analyze_price_strategy(params, current_sales)
        if price_rec:
            recommendations.append(price_rec)

        # 2. 促销建议
        promotion_rec = self._analyze_promotion_strategy(params, current_sales)
        if promotion_rec:
            recommendations.append(promotion_rec)

        # 3. 季节性建议
        seasonal_rec = self._analyze_seasonal_strategy(params, current_sales)
        if seasonal_rec:
            recommendations.append(seasonal_rec)

        # 4. 竞争策略
        competitor_rec = self._analyze_competitor_strategy(params, current_sales)
        if competitor_rec:
            recommendations.append(competitor_rec)

        # 计算最优策略
        best_strategy = self._find_optimal_strategy(params)

        return {
            'current_prediction': current_prediction,
            'recommendations': recommendations,
            'best_strategy': best_strategy,
            'risk_level': self._assess_risk(params)
        }

    def _analyze_price_strategy(self, params: Dict, current_sales: int) -> Dict:
        """价格策略分析"""
        price = params.get('price', 15.0)
        competitor_price = params.get('competitor_price', 16.0)

        if price > competitor_price * 1.1:
            # 测试降价效果
            test_params = params.copy()
            test_params['price'] = competitor_price * 0.95
            test_prediction = self.prediction_engine.predict(test_params)
            potential_increase = test_prediction['predicted_sales'] - current_sales

            return {
                'type': 'price',
                'priority': 'high',
                'title': '价格竞争力不足',
                'description': f'当前价格({price}万)高于竞品({competitor_price}万)，建议适当降价',
                'action': f'降价至 {competitor_price * 0.95:.1f}万',
                'expected_impact': f'+{potential_increase}辆 (+{potential_increase/current_sales*100:.1f}%)',
                'confidence': 'high'
            }
        elif price < competitor_price * 0.9:
            return {
                'type': 'price',
                'priority': 'medium',
                'title': '价格优势明显',
                'description': f'当前价格具有竞争力，可考虑小幅提价增加利润',
                'action': f'提价至 {min(price * 1.05, competitor_price * 0.95):.1f}万',
                'expected_impact': '保持销量同时提升利润',
                'confidence': 'medium'
            }
        return None

    def _analyze_promotion_strategy(self, params: Dict, current_sales: int) -> Dict:
        """促销策略分析"""
        promotion = params.get('promotion', 5.0)
        month = params.get('month', datetime.now().month)

        # 淡季加大促销
        if month in [1, 2, 7, 8, 9] and promotion < 7:
            test_params = params.copy()
            test_params['promotion'] = 8.0
            test_prediction = self.prediction_engine.predict(test_params)
            potential_increase = test_prediction['predicted_sales'] - current_sales

            return {
                'type': 'promotion',
                'priority': 'high',
                'title': '淡季促销机会',
                'description': f'{month}月为销售淡季，建议加大促销力度',
                'action': '提升促销力度至 8/10',
                'expected_impact': f'+{potential_increase}辆 (+{potential_increase/current_sales*100:.1f}%)',
                'confidence': 'high',
                'suggested_activities': [
                    '限时优惠活动',
                    '以旧换新补贴',
                    '金融贴息方案',
                    '赠送保养套餐'
                ]
            }
        return None

    def _analyze_seasonal_strategy(self, params: Dict, current_sales: int) -> Dict:
        """季节性策略分析"""
        month = params.get('month', datetime.now().month)

        # 旺季准备
        if month in [3, 4, 5, 6]:
            return {
                'type': 'seasonal',
                'priority': 'medium',
                'title': '销售旺季',
                'description': f'{month}月为销售旺季，需做好库存和服务准备',
                'action': '优化供应链和服务体系',
                'recommendations': [
                    '增加库存储备',
                    '加强销售团队培训',
                    '优化交付流程',
                    '提升售后服务能力'
                ],
                'confidence': 'high'
            }
        return None

    def _analyze_competitor_strategy(self, params: Dict, current_sales: int) -> Dict:
        """竞争策略分析"""
        price = params.get('price', 15.0)
        competitor_price = params.get('competitor_price', 16.0)
        promotion = params.get('promotion', 5.0)

        price_gap = (price - competitor_price) / competitor_price * 100

        if abs(price_gap) < 5 and promotion < 6:
            return {
                'type': 'competitor',
                'priority': 'medium',
                'title': '差异化竞争建议',
                'description': '价格与竞品接近，建议通过服务和品牌差异化竞争',
                'action': '强化品牌价值和服务优势',
                'strategies': [
                    '突出产品独特卖点',
                    '提供更优质的售后服务',
                    '建立品牌社区和用户口碑',
                    '开展试驾体验活动'
                ],
                'confidence': 'medium'
            }
        return None

    def _find_optimal_strategy(self, params: Dict) -> Dict:
        """寻找最优策略组合"""
        base_params = params.copy()
        current_pred = self.prediction_engine.predict(base_params)
        current_sales = current_pred['predicted_sales']

        # 测试不同策略组合
        strategies = []

        # 策略1: 降价 + 高促销
        test1 = params.copy()
        test1['price'] = params.get('price', 15.0) * 0.95
        test1['promotion'] = 8.0
        pred1 = self.prediction_engine.predict(test1)
        strategies.append({
            'name': '降价促销策略',
            'params': {'price_change': '-5%', 'promotion': 8},
            'predicted_sales': pred1['predicted_sales'],
            'increase': pred1['predicted_sales'] - current_sales,
            'increase_pct': (pred1['predicted_sales'] - current_sales) / current_sales * 100
        })

        # 策略2: 保持价格 + 超高促销
        test2 = params.copy()
        test2['promotion'] = 9.0
        pred2 = self.prediction_engine.predict(test2)
        strategies.append({
            'name': '强促销策略',
            'params': {'price_change': '0%', 'promotion': 9},
            'predicted_sales': pred2['predicted_sales'],
            'increase': pred2['predicted_sales'] - current_sales,
            'increase_pct': (pred2['predicted_sales'] - current_sales) / current_sales * 100
        })

        # 策略3: 小幅降价 + 中等促销
        test3 = params.copy()
        test3['price'] = params.get('price', 15.0) * 0.97
        test3['promotion'] = 7.0
        pred3 = self.prediction_engine.predict(test3)
        strategies.append({
            'name': '平衡策略',
            'params': {'price_change': '-3%', 'promotion': 7},
            'predicted_sales': pred3['predicted_sales'],
            'increase': pred3['predicted_sales'] - current_sales,
            'increase_pct': (pred3['predicted_sales'] - current_sales) / current_sales * 100
        })

        # 找到最优策略
        best = max(strategies, key=lambda x: x['predicted_sales'])

        return {
            'recommended': best,
            'alternatives': [s for s in strategies if s != best],
            'current_baseline': {
                'predicted_sales': current_sales
            }
        }

    def _assess_risk(self, params: Dict) -> Dict:
        """风险评估"""
        price = params.get('price', 15.0)
        economy_index = params.get('economy_index', 70.0)
        competitor_price = params.get('competitor_price', 16.0)

        risks = []
        risk_score = 0

        # 价格风险
        if price > competitor_price * 1.15:
            risks.append('价格过高，可能失去市场竞争力')
            risk_score += 30

        # 经济风险
        if economy_index < 60:
            risks.append('经济指数偏低，市场需求可能下降')
            risk_score += 25

        # 季节风险
        month = params.get('month', datetime.now().month)
        if month in [1, 2, 8, 9]:
            risks.append('当前处于销售淡季')
            risk_score += 15

        if risk_score > 50:
            level = 'high'
        elif risk_score > 25:
            level = 'medium'
        else:
            level = 'low'

        return {
            'level': level,
            'score': risk_score,
            'risks': risks,
            'mitigation': self._get_risk_mitigation(risks)
        }

    def _get_risk_mitigation(self, risks: List[str]) -> List[str]:
        """风险缓解建议"""
        mitigations = []
        if '价格过高' in str(risks):
            mitigations.append('调整价格策略，提供分期付款方案')
        if '经济指数偏低' in str(risks):
            mitigations.append('关注目标客户群体，精准营销')
        if '销售淡季' in str(risks):
            mitigations.append('加大促销力度，推出限时优惠')
        return mitigations


# 全局实例
recommendation_engine = RecommendationEngine()
