"""FastAPI 中介軟體"""
import time
import logging
from typing import Callable
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.exceptions import CourseAIException

logger = logging.getLogger(__name__)


class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    """全域錯誤處理中介軟體"""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        try:
            response = await call_next(request)
            return response

        except CourseAIException as e:
            # 記錄自定義異常
            logger.warning(
                f"CourseAI Exception: {e.error_code} - {e.message}",
                extra={
                    "error_code": e.error_code,
                    "status_code": e.status_code,
                    "details": e.details,
                    "path": request.url.path,
                },
            )

            return JSONResponse(
                status_code=e.status_code,
                content={
                    "error": e.error_code,
                    "message": e.message,
                    "details": e.details,
                },
            )

        except Exception as e:
            # 記錄未預期的異常
            logger.error(
                f"Unexpected error: {str(e)}",
                exc_info=True,
                extra={"path": request.url.path},
            )

            return JSONResponse(
                status_code=500,
                content={
                    "error": "INTERNAL_SERVER_ERROR",
                    "message": "An unexpected error occurred",
                    "details": {},
                },
            )


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """請求日誌中介軟體"""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # 記錄請求開始
        start_time = time.time()

        # 處理請求
        response = await call_next(request)

        # 計算處理時間
        process_time = time.time() - start_time

        # 記錄請求完成
        logger.info(
            f"{request.method} {request.url.path}",
            extra={
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "process_time": f"{process_time:.3f}s",
                "client_ip": request.client.host if request.client else None,
            },
        )

        # 添加處理時間到響應標頭
        response.headers["X-Process-Time"] = f"{process_time:.3f}"

        return response


class CORSHeadersMiddleware(BaseHTTPMiddleware):
    """CORS 標頭中介軟體（補充）"""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)

        # 添加安全標頭
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"

        return response
