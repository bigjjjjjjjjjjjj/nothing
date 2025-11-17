"""自定義異常類別"""
from typing import Any, Dict, Optional


class CourseAIException(Exception):
    """CourseAI 基礎異常"""

    def __init__(
        self,
        message: str,
        status_code: int = 500,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code or self.__class__.__name__
        self.details = details or {}
        super().__init__(self.message)


class ValidationError(CourseAIException):
    """驗證錯誤"""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            status_code=422,
            error_code="VALIDATION_ERROR",
            details=details,
        )


class NotFoundError(CourseAIException):
    """資源不存在錯誤"""

    def __init__(self, resource: str, identifier: str):
        super().__init__(
            message=f"{resource} '{identifier}' not found",
            status_code=404,
            error_code="NOT_FOUND",
            details={"resource": resource, "identifier": identifier},
        )


class AuthenticationError(CourseAIException):
    """認證錯誤"""

    def __init__(self, message: str = "Authentication failed"):
        super().__init__(
            message=message,
            status_code=401,
            error_code="AUTHENTICATION_ERROR",
        )


class AuthorizationError(CourseAIException):
    """授權錯誤"""

    def __init__(self, message: str = "Permission denied"):
        super().__init__(
            message=message,
            status_code=403,
            error_code="AUTHORIZATION_ERROR",
        )


class DatabaseError(CourseAIException):
    """資料庫錯誤"""

    def __init__(self, message: str, original_error: Optional[Exception] = None):
        super().__init__(
            message=message,
            status_code=500,
            error_code="DATABASE_ERROR",
            details={"original_error": str(original_error)} if original_error else {},
        )


class ExternalAPIError(CourseAIException):
    """外部 API 錯誤"""

    def __init__(
        self, service: str, message: str, original_error: Optional[Exception] = None
    ):
        super().__init__(
            message=f"{service} API error: {message}",
            status_code=502,
            error_code="EXTERNAL_API_ERROR",
            details={
                "service": service,
                "original_error": str(original_error) if original_error else None,
            },
        )


class FileProcessingError(CourseAIException):
    """檔案處理錯誤"""

    def __init__(self, message: str, filename: Optional[str] = None):
        super().__init__(
            message=message,
            status_code=400,
            error_code="FILE_PROCESSING_ERROR",
            details={"filename": filename} if filename else {},
        )


class RateLimitError(CourseAIException):
    """請求限流錯誤"""

    def __init__(self, message: str = "Rate limit exceeded", retry_after: int = 60):
        super().__init__(
            message=message,
            status_code=429,
            error_code="RATE_LIMIT_ERROR",
            details={"retry_after": retry_after},
        )


class WebSocketError(CourseAIException):
    """WebSocket 錯誤"""

    def __init__(self, message: str):
        super().__init__(
            message=message,
            status_code=400,
            error_code="WEBSOCKET_ERROR",
        )
