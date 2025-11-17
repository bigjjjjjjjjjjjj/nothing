"""日誌配置"""
import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler
from app.core.config import settings


def setup_logging():
    """設置應用日誌系統"""

    # 建立 logs 目錄
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    # 設置根日誌器
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, settings.LOG_LEVEL))

    # 清除現有的處理器
    root_logger.handlers.clear()

    # 格式化器
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # 控制台處理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # 文件處理器（輪替）
    file_handler = RotatingFileHandler(
        settings.LOG_FILE,
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)

    # 錯誤日誌處理器
    error_handler = RotatingFileHandler(
        log_dir / "error.log",
        maxBytes=10 * 1024 * 1024,
        backupCount=5,
        encoding='utf-8'
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)
    root_logger.addHandler(error_handler)

    # 設置第三方庫的日誌級別
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("sqlalchemy").setLevel(logging.WARNING)
    logging.getLogger("asyncio").setLevel(logging.WARNING)

    logging.info("日誌系統已初始化")
    logging.info(f"日誌級別: {settings.LOG_LEVEL}")
    logging.info(f"日誌文件: {settings.LOG_FILE}")
