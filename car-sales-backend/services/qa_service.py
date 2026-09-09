# ============================================================
# 文件路径：car-sales-backend/services/qa_service.py
# 作用：智能问答服务（本地知识库 + 项目数据问答）
#   1. 数据问答：基于 SQLite 中的销量/预测数据实时计算回答
#   2. 知识库问答：内置汽车行业知识库（新能源、购车、市场、政策等）
#   3. 兜底回答：提示用户可以问什么问题
# ============================================================

import re
from sqlalchemy import func
from models.sales import SalesRecord, PredictionRecord, QueryLog
from core.database import SessionLocal


# ---------------- 汽车行业知识库 ----------------
# 每条：keywords 命中关键词，answer 回答文本
KNOWLEDGE_BASE = [
    {
        "topic": "新能源汽车",
        "keywords": ["新能源", "电动车", "电动汽车", "纯电", "混动", "插混", "增程", "电池", "续航"],
        "answer": (
            "新能源汽车主要包括纯电动汽车（BEV）、插电式混合动力（PHEV）和增程式（EREV）三类。\n"
            "选购建议：\n"
            "· 纯电：日常通勤、家里能装充电桩、有长途需求但可接受规划充电，选续航 500km+ 的车型；\n"
            "· 插混/增程：充电不便或经常跑长途，可用油可用电，无续航焦虑；\n"
            "· 电池：主流是磷酸铁锂（安全、寿命长、成本低）和三元锂（能量密度高、低温表现好）；\n"
            "· 充电：家用慢充（7kW）充满一般 6-10 小时，公共快充（120kW+）30 分钟可充 30%-80%。"
        ),
    },
    {
        "topic": "燃油车",
        "keywords": ["燃油车", "汽油车", "油车", "发动机", "排量", "涡轮"],
        "answer": (
            "燃油车主要看发动机、变速箱和底盘三大件：\n"
            "· 发动机：自然吸气平顺耐用，涡轮增压动力强、省油（市区选 1.5T 左右足够，高速多选 2.0T）；\n"
            "· 变速箱：AT（爱信/采埃孚）平顺可靠，双离合换挡快但低速可能顿挫，CVT 最平顺但大扭矩场景偏弱；\n"
            "· 油耗：1.5L 自吸市区约 7-8L/100km，2.0T 约 9-11L/100km，混动燃油车可低至 5L 左右。"
        ),
    },
    {
        "topic": "购车预算与选车",
        "keywords": ["预算", "选车", "买车", "购车", "推荐", "哪款", "性价比", "家用", "代步"],
        "answer": (
            "按预算的通用选车思路：\n"
            "· 8-12 万：家用代步看比亚迪秦/海鸥、日产轩逸、大众朗逸，性价比高、保值率稳；\n"
            "· 12-18 万：混动看比亚迪宋、银河 L7；纯电看小鹏 MONA、埃安；燃油看速腾、思域、星越 L；\n"
            "· 18-25 万：新能源看特斯拉 Model 3、极氪 007、小米 SU7；燃油看凯美瑞、帕萨特、CR-V；\n"
            "· 25 万以上：豪华品牌看宝马 3 系/奥迪 A4、理想 L6/L7、问界 M7。\n"
            "核心原则：先定预算上限，再定用车场景（通勤/长途/家庭），最后对比同价位 3-4 款车型的能耗、空间和售后。"
        ),
    },
    {
        "topic": "汽车销量市场",
        "keywords": ["销量市场", "市场份额", "品牌销量", "卖得好", "销量排行", "排行榜", "热销"],
        "answer": (
            "当前国内汽车市场格局（近年趋势）：\n"
            "· 新能源渗透率已超过 50%，新能源车成为新车销售主流；\n"
            "· 头部品牌：比亚迪稳居新能源销量第一，特斯拉、吉利/极氪、长安、奇瑞、理想、问界（鸿蒙智行）紧随其后；\n"
            "· 热销车型集中在 10-20 万价格带，SUV 与轿车并重，插混车型增速最快；\n"
            "· 合资品牌燃油车市场份额持续承压，价格战频繁。\n"
            "（具体月度数据可在本系统的“数据可视化”页面查看。）"
        ),
    },
    {
        "topic": "汽车购置政策",
        "keywords": ["购置税", "补贴", "政策", "以旧换新", "免购置税", "国补", "地方补贴"],
        "answer": (
            "购车相关政策要点：\n"
            "· 新能源车免征车辆购置税政策持续实施（单车免税额上限约 3 万元）；\n"
            "· 以旧换新补贴：报废或置换旧车购买新车可申请国家补贴（新能源车与燃油车补贴标准不同）；\n"
            "· 部分地区还有地方消费券/置换补贴，可与国家补贴叠加；\n"
            "· 政策会随年度调整，购车前建议查询当年最新的补贴目录与标准。"
        ),
    },
    {
        "topic": "汽车金融与保险",
        "keywords": ["贷款", "分期", "保险", "车险", "首付", "月供", "全款"],
        "answer": (
            "购车付款与保险建议：\n"
            "· 贷款：主流 2-5 年分期，首付 20%-30%，注意看清“年化利率”（换算成 IRR 比较真实成本）；\n"
            "· 保险：交强险必买，商业险建议车损险 + 三者险（200 万以上）+ 座位险；新能源车保费普遍高于同级燃油车；\n"
            "· 全款 vs 贷款：全款省利息和手续费；若贷款有免息政策且现金流有更好去处，分期更划算。"
        ),
    },
    {
        "topic": "二手车",
        "keywords": ["二手车", "二手", "保值率", "过户"],
        "answer": (
            "二手车选购要点：\n"
            "· 保值率：日系（丰田/本田）和热门车型保值率高，新能源车保值率普遍偏低、但近年有所改善；\n"
            "· 验车：查维保记录、事故记录（出险记录），重点看底盘、纵梁、ABC 柱有无修复痕迹；\n"
            "· 流程：确认无抵押、手续齐全（行驶证、登记证书、完税证明），签合同注明车况与退车条款；\n"
            "· 建议请第三方检测机构出具检测报告。"
        ),
    },
    {
        "topic": "汽车保养",
        "keywords": ["保养", "机油", "首保", "大保养", "轮胎", "更换"],
        "answer": (
            "汽车保养周期参考：\n"
            "· 机油机滤：全合成机油约 1 万公里/1 年一换，半合成 5000-7500 公里；\n"
            "· 空气滤芯/空调滤芯：1-2 万公里更换，污染重地区缩短；\n"
            "· 刹车油：2 年或 4 万公里；防冻液：2-4 年；火花塞：3-6 万公里；\n"
            "· 轮胎：5 年或 6-8 万公里，出现裂纹/鼓包立即更换；\n"
            "· 新能源车：主要保养三电系统（电池、电机、电控），费用远低于燃油车，但仍需定期检查。"
        ),
    },
    {
        "topic": "驾驶与安全",
        "keywords": ["安全", "气囊", "辅助驾驶", "智驾", "自动泊车", "L2", "acc"],
        "answer": (
            "汽车安全与智能驾驶常识：\n"
            "· 被动安全：看车身结构（笼式车身）、安全气囊数量、安全带预紧，参考 C-NCAP / 中保研碰撞成绩；\n"
            "· 主动安全：AEB 自动紧急制动、车道保持（LKA）、盲区监测（BSD）能显著降低事故率；\n"
            "· 智能驾驶分级：L2（辅助驾驶，需驾驶员随时接管）为当前主流；L3+ 高阶智驾（高速 NOA/城市 NOA）正快速普及；\n"
            "· 使用智驾时务必保持注意力，系统只是辅助。"
        ),
    },
    {
        "topic": "汽车品牌",
        "keywords": ["品牌", "比亚迪", "特斯拉", "大众", "丰田", "本田", "宝马", "奔驰", "奥迪", "吉利", "奇瑞", "长城", "理想", "蔚来", "小鹏", "小米", "问界", "长安", "日产", "别克", "现代"],
        "answer": (
            "主流汽车品牌定位速览：\n"
            "· 新能源头部：比亚迪（全价位覆盖）、特斯拉（纯电标杆）、吉利/极氪、长安深蓝/阿维塔、奇瑞、理想（家庭增程）、蔚来（换电+服务）、小鹏（智驾）、小米（年轻智能）、问界（华为智驾）；\n"
            "· 传统合资：大众、丰田、本田、日产、别克——燃油车体系成熟、售后网点多，正在加速电动化转型；\n"
            "· 豪华品牌：奔驰（舒适豪华）、宝马（操控）、奥迪（科技均衡）；\n"
            "· 选择逻辑：新能源看重三电与智能化，燃油车看重机械素质与保值率，按自己用车场景决定。"
        ),
    },
    {
        "topic": "停车与用车成本",
        "keywords": ["停车", "用车成本", "养车", "油费", "电费", "成本"],
        "answer": (
            "用车成本构成：\n"
            "· 燃油车：按 8L/100km、92 号 7.5 元/L 算，每公里约 0.6 元；\n"
            "· 电动车：家充 0.5-0.6 元/度，百公里 13-15 度电，每公里约 0.08-0.1 元，仅为燃油的 1/6；\n"
            "· 保险：新能源车首年保费通常比同级燃油车高 10%-30%；\n"
            "· 保养：燃油车年均 1500-3000 元，新能源车年均 500-1000 元；\n"
            "· 停车/过路费两车相同；综合计算，年行驶 1.5 万公里时电车每年约省 6000-9000 元。"
        ),
    },
    {
        "topic": "汽车类型",
        "keywords": ["suv", "轿车", "mpv", "轿跑", "车型", "空间", "两厢", "三厢"],
        "answer": (
            "主要车型类型选择：\n"
            "· 轿车：重心低、操控好、风阻小省油，适合城市通勤与高速；\n"
            "· SUV：空间大、通过性好、视野高，适合家庭与多路况，但油耗/电耗略高；\n"
            "· MPV：7 座布局、第二排舒适度高，适合多孩家庭与商务接待；\n"
            "· 轿跑/旅行车：兼顾颜值与实用，偏个性化需求；\n"
            "· 选型口诀：重操控选轿车，重空间选 SUV，重乘坐选 MPV。"
        ),
    },
]


# ---------------- 数据问答 ----------------
def _get_stats(db):
    """从数据库聚合销量统计"""
    total = db.query(func.sum(SalesRecord.sales)).scalar() or 0
    count = db.query(func.count(SalesRecord.id)).scalar() or 0
    avg = round(total / count) if count else 0
    peak = db.query(SalesRecord).order_by(SalesRecord.sales.desc()).first()
    trough = db.query(SalesRecord).order_by(SalesRecord.sales.asc()).first()
    latest = db.query(SalesRecord).order_by(SalesRecord.date.desc()).first()
    return {
        "total": int(total), "count": count, "avg": avg,
        "peak": {"date": peak.date, "sales": peak.sales} if peak else None,
        "trough": {"date": trough.date, "sales": trough.sales} if trough else None,
        "latest": {"date": latest.date, "sales": latest.sales} if latest else None,
    }


def _answer_data_question(question: str, db) -> dict | None:
    """尝试用项目数据回答，命中返回 {answer, topic, data}，否则 None"""
    q = question.lower()

    # 数据库/日志相关问题
    if any(k in q for k in ["数据库", "日志", "查询记录", "几条记录", "多少条"]):
        recs = db.query(func.count(SalesRecord.id)).scalar() or 0
        preds = db.query(func.count(PredictionRecord.id)).scalar() or 0
        logs = db.query(func.count(QueryLog.id)).scalar() or 0
        return {
            "topic": "项目数据 · 数据库",
            "answer": (
                f"当前系统数据库共 3 张表：\n"
                f"· 销量数据表 sales_records：{recs} 条月度销量记录\n"
                f"· 预测结果表 prediction_records：{preds} 条未来预测\n"
                f"· 查询日志表 query_logs：{logs} 条（每次访问接口都会自动记录）"
            ),
            "data": {"sales_records": recs, "prediction_records": preds, "query_logs": logs},
        }

    # 未来预测问题
    if any(k in q for k in ["预测", "未来", "下个月", "接下来", "走势如何", "趋势如何", "会怎样"]):
        preds = db.query(PredictionRecord).order_by(PredictionRecord.date.asc()).all()
        if preds:
            first, last = preds[0], preds[-1]
            avg_f = sum(p.forecast for p in preds) / len(preds)
            trend = "上升" if last.forecast >= first.forecast else "下降"
            lines = [f"· {p.date}：{round(p.forecast)} 辆" for p in preds[:6]]
            if len(preds) > 6:
                lines.append(f"· ……（共 {len(preds)} 个月，完整见“模型预测”页）")
            return {
                "topic": "项目数据 · 销量预测",
                "answer": (
                    f"根据时间序列模型，未来 12 个月平均预测销量约 {round(avg_f)} 辆，整体呈{trend}趋势：\n"
                    + "\n".join(lines)
                ),
                "data": {"count": len(preds), "avg_forecast": round(avg_f)},
            }

    # 趋势问题
    if any(k in q for k in ["趋势", "增长", "上升", "下降", "涨", "跌"]):
        stats = _get_stats(db)
        return {
            "topic": "项目数据 · 销量趋势",
            "answer": (
                f"历史数据集共 {stats['count']} 个月（{stats['latest']['date']} 为止）：\n"
                f"· 累计销量 {stats['total']:,} 辆，月均 {stats['avg']:,} 辆\n"
                f"· 峰值出现在 {stats['peak']['date']}（{stats['peak']['sales']:,} 辆）\n"
                f"· 低点出现在 {stats['trough']['date']}（{stats['trough']['sales']:,} 辆）\n"
                f"· 最新一期（{stats['latest']['date']}）销量 {stats['latest']['sales']:,} 辆\n"
                f"整体趋势与季节性波动可查看“数据可视化”页面的趋势图。"
            ),
            "data": stats,
        }

    # 统计类问题（总/平均/最多/最少/某月）
    if any(k in q for k in ["销量", "统计", "总共", "一共", "平均", "最多", "最少", "最高", "最低", "峰值", "低谷", "多少"]):
        stats = _get_stats(db)
        m = re.search(r"(\d{4})[-年](\d{1,2})", question)
        if m:
            date_prefix = f"{m.group(1)}-{int(m.group(2)):02d}"
            rec = db.query(SalesRecord).filter(SalesRecord.date.like(date_prefix + "%")).first()
            if rec:
                return {
                    "topic": "项目数据 · 单月销量",
                    "answer": f"{rec.date} 的汽车销量为 {rec.sales:,} 辆。",
                    "data": {"date": rec.date, "sales": rec.sales},
                }
        return {
            "topic": "项目数据 · 销量统计",
            "answer": (
                f"历史数据统计（{stats['count']} 个月）：\n"
                f"· 累计销量：{stats['total']:,} 辆\n"
                f"· 月均销量：{stats['avg']:,} 辆\n"
                f"· 销量峰值：{stats['peak']['date']}，{stats['peak']['sales']:,} 辆\n"
                f"· 销量低谷：{stats['trough']['date']}，{stats['trough']['sales']:,} 辆"
            ),
            "data": stats,
        }

    return None


def _answer_knowledge(question: str) -> dict | None:
    """知识库关键词匹配，按命中数打分"""
    best, best_score = None, 0
    for item in KNOWLEDGE_BASE:
        score = sum(1 for kw in item["keywords"] if kw.lower() in question.lower())
        if score > best_score:
            best, best_score = item, score
    if best and best_score > 0:
        return {"topic": "汽车知识 · " + best["topic"], "answer": best["answer"]}
    return None


FALLBACK_ANSWER = (
    "这个问题我暂时没法直接回答。我可以帮你解答两类问题：\n"
    "1. 项目数据类：例如“总销量是多少”“哪个月销量最高”“未来预测趋势如何”\n"
    "2. 汽车知识类：例如“新能源车怎么选”“10 万预算买什么车”“汽车保养多久一次”\n"
    "试试换个问法，或者点击下方推荐问题直接提问。"
)


def ask(question: str, db=None) -> dict:
    """问答入口：数据问答 → 知识库问答 → 兜底"""
    question = (question or "").strip()
    if not question:
        return {"answer": "请输入您想了解的问题。", "topic": "提示", "matched": False}

    own_db = db is None
    if own_db:
        db = SessionLocal()
    try:
        # 1) 数据问答
        r = _answer_data_question(question, db)
        if r:
            return {"answer": r["answer"], "topic": r["topic"], "matched": True, "data": r.get("data")}
        # 2) 知识库问答
        r = _answer_knowledge(question)
        if r:
            return {"answer": r["answer"], "topic": r["topic"], "matched": True}
        # 3) 兜底
        return {"answer": FALLBACK_ANSWER, "topic": "未匹配", "matched": False}
    finally:
        if own_db:
            db.close()


# 推荐问题（前端展示用）
SUGGESTED_QUESTIONS = [
    "新能源车和燃油车怎么选？",
    "10 万预算买什么车好？",
    "本系统销量数据有多少条？",
    "历史销量最高的月份是哪个？",
    "未来销量预测趋势如何？",
    "汽车多久保养一次？",
]
