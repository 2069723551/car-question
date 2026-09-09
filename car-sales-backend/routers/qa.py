# ============================================================
# 文件路径：car-sales-backend/routers/qa.py
# 作用：智能问答接口
#   POST /api/qa/ask       提出问题，返回回答
#   GET  /api/qa/suggest   获取推荐问题
# ============================================================

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from core.database import get_db
from services import qa_service
from models.sales import QueryLog

router = APIRouter(prefix="/api/qa", tags=["智能问答"])


class AskRequest(BaseModel):
    question: str


@router.post("/ask")
def ask(req: AskRequest, db: Session = Depends(get_db)):
    """接收问题，返回智能回答（数据问答 / 知识库问答）"""
    result = qa_service.ask(req.question, db)

    # 记录查询日志
    try:
        log = QueryLog(endpoint="/api/qa/ask", method="POST", status="success")
        db.add(log)
        db.commit()
    except Exception:
        db.rollback()

    return {"success": True, "question": req.question, **result}


@router.get("/suggest")
def suggest():
    """推荐问题列表"""
    return {"success": True, "questions": qa_service.SUGGESTED_QUESTIONS}
