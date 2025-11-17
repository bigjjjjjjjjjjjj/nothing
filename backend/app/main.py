"""FastAPI 主應用"""
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.config import settings
from app.core.database import init_db, close_db
from app.core.logging_config import setup_logging
from app.api import courses, quizzes, transcripts, teacher_hints

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """應用生命週期管理"""
    # 啟動時執行
    setup_logging()
    logger.info("Starting CourseAI API Server...")
    await init_db()
    logger.info("Database initialized")

    yield

    # 關閉時執行
    logger.info("Shutting down CourseAI API Server...")
    await close_db()
    logger.info("Database connections closed")


# 建立 FastAPI 應用
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="CourseAI 智慧學習助理 - 後端 API 服務",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS 中間件設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 健康檢查
@app.get("/health")
async def health_check():
    """健康檢查端點"""
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
    }


@app.get("/")
async def root():
    """根路徑"""
    return {
        "message": "CourseAI API Server",
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "health": "/health",
    }


# 註冊 API 路由
app.include_router(
    courses.router,
    prefix=f"{settings.API_PREFIX}/courses",
    tags=["Courses"]
)
app.include_router(
    quizzes.router,
    prefix=f"{settings.API_PREFIX}/quizzes",
    tags=["Quizzes"]
)
app.include_router(
    transcripts.router,
    prefix=f"{settings.API_PREFIX}/transcripts",
    tags=["Transcripts"]
)
app.include_router(
    teacher_hints.router,
    prefix=f"{settings.API_PREFIX}/teacher-hints",
    tags=["Teacher Hints"]
)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.DEBUG,
    )
