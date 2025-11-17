"""應用配置管理"""
from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """應用設定"""

    # 應用資訊
    APP_NAME: str = "CourseAI"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "production"

    # API 設定
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    API_PREFIX: str = "/api/v1"

    # 資料庫設定
    DATABASE_URL: str = Field(
        default="postgresql+asyncpg://courseai:password@localhost:5432/courseai",
        description="資料庫連線 URL"
    )
    DATABASE_ECHO: bool = False

    # Redis 設定
    REDIS_URL: str = "redis://localhost:6379/0"

    # JWT 設定
    SECRET_KEY: str = Field(
        default="change-this-secret-key-in-production",
        description="JWT 加密金鑰"
    )
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # CORS 設定
    CORS_ORIGINS: List[str] = [
        "https://meet.google.com",
        "chrome-extension://*"
    ]

    # Google Cloud 設定
    GOOGLE_APPLICATION_CREDENTIALS: Optional[str] = None
    GOOGLE_CLOUD_PROJECT: Optional[str] = None
    GOOGLE_CLOUD_BUCKET: Optional[str] = None

    # OpenAI / LLM 設定
    OPENAI_API_KEY: Optional[str] = None
    LLM_MODEL: str = "gpt-4"
    LLM_TEMPERATURE: float = 0.7
    LLM_MAX_TOKENS: int = 2000

    # Whisper 設定
    WHISPER_MODEL: str = "base"
    USE_GOOGLE_SPEECH: bool = True

    # Celery 設定
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"

    # 檔案上傳設定
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_EXTENSIONS: List[str] = ["pdf", "ppt", "pptx", "doc", "docx"]
    UPLOAD_DIR: str = "uploads"

    # WebSocket 設定
    WS_HEARTBEAT_INTERVAL: int = 30
    WS_MAX_CONNECTIONS: int = 1000

    # 日誌設定
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/app.log"

    class Config:
        env_file = ".env"
        case_sensitive = True


# 建立全域設定實例
settings = Settings()
