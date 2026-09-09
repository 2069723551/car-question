from pathlib import Path
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from routers import sales, prediction, qa, news, charts, ranking, cars
from services.db_service import startup_init
from core.config import FIGURES_DIR, FRONTEND_DIR

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

logger.info("正在初始化数据库...")
startup_init()

app = FastAPI(
    title="汽车销量预测系统 API",
    description="销量数据采集与预处理、特征工程、销量预测模型、预测结果可视化、智能预测与推荐、智能问答",
    version="2.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(sales.router)
app.include_router(prediction.router)
app.include_router(qa.router)
app.include_router(news.router)
app.include_router(charts.router)
app.include_router(ranking.router)
app.include_router(cars.router)

FIGURES_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/figures", StaticFiles(directory=FIGURES_DIR), name="figures")

if FRONTEND_DIR.is_dir() and (FRONTEND_DIR / "assets").is_dir():
    app.mount("/assets", StaticFiles(directory=FRONTEND_DIR / "assets"), name="frontend-assets")


@app.get("/api/health")
async def health():
    return {"status": "ok", "service": "car-sales"}


@app.get("/")
async def root():
    index_file = FRONTEND_DIR / "index.html"
    if index_file.is_file():
        return FileResponse(index_file)
    return {
        "message": "汽车销量预测系统后端已启动（SQLite 数据库版）",
        "docs": "/docs",
        "frontend": "同域前端尚未构建，请先执行 npm run build",
        "database": "sqlite:///car_sales.db",
    }


@app.get("/{path:path}")
async def frontend_fallback(path: str):
    if FRONTEND_DIR.is_dir():
        frontend_root = FRONTEND_DIR.resolve()
        requested_file = (frontend_root / Path(path)).resolve()
        if requested_file.is_relative_to(frontend_root) and requested_file.is_file():
            return FileResponse(requested_file)
        index_file = frontend_root / "index.html"
        if index_file.is_file():
            return FileResponse(index_file)
    return JSONResponse({"detail": "Not Found"}, status_code=404)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)