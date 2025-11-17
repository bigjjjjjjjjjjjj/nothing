"""驗證工具函數"""
import re
from typing import List, Optional
from app.core.exceptions import ValidationError


def validate_email(email: str) -> str:
    """驗證電子郵件格式"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(pattern, email):
        raise ValidationError(
            message="Invalid email format",
            details={"email": email}
        )
    return email


def validate_file_extension(filename: str, allowed_extensions: List[str]) -> str:
    """驗證檔案副檔名"""
    extension = filename.split('.')[-1].lower()
    if extension not in allowed_extensions:
        raise ValidationError(
            message=f"File extension '.{extension}' not allowed",
            details={
                "filename": filename,
                "allowed_extensions": allowed_extensions
            }
        )
    return extension


def validate_file_size(file_size: int, max_size: int) -> None:
    """驗證檔案大小"""
    if file_size > max_size:
        raise ValidationError(
            message=f"File size ({file_size} bytes) exceeds maximum ({max_size} bytes)",
            details={
                "file_size": file_size,
                "max_size": max_size,
                "max_size_mb": max_size / (1024 * 1024)
            }
        )


def validate_meeting_id(meeting_id: str) -> str:
    """驗證 Google Meet 會議 ID 格式"""
    # Google Meet ID 通常是 xxx-xxxx-xxx 格式
    pattern = r'^[a-z]{3}-[a-z]{4}-[a-z]{3}$'
    if not re.match(pattern, meeting_id):
        # 也接受其他格式的會議 ID
        if len(meeting_id) < 3 or len(meeting_id) > 50:
            raise ValidationError(
                message="Invalid meeting ID format",
                details={"meeting_id": meeting_id}
            )
    return meeting_id


def validate_pagination(skip: int = 0, limit: int = 100, max_limit: int = 1000) -> tuple:
    """驗證分頁參數"""
    if skip < 0:
        raise ValidationError(
            message="Skip must be non-negative",
            details={"skip": skip}
        )

    if limit < 1:
        raise ValidationError(
            message="Limit must be at least 1",
            details={"limit": limit}
        )

    if limit > max_limit:
        raise ValidationError(
            message=f"Limit cannot exceed {max_limit}",
            details={"limit": limit, "max_limit": max_limit}
        )

    return skip, limit


def sanitize_html(text: str) -> str:
    """清理 HTML 標籤（簡單版本）"""
    # 移除 HTML 標籤
    clean_text = re.sub(r'<[^>]+>', '', text)
    # 移除多餘空白
    clean_text = ' '.join(clean_text.split())
    return clean_text


def validate_difficulty(difficulty: str) -> str:
    """驗證難度等級"""
    valid_difficulties = ['easy', 'medium', 'hard']
    if difficulty not in valid_difficulties:
        raise ValidationError(
            message="Invalid difficulty level",
            details={
                "difficulty": difficulty,
                "valid_values": valid_difficulties
            }
        )
    return difficulty


def validate_language_code(lang_code: str) -> str:
    """驗證語言代碼"""
    # ISO 639-1 語言代碼
    valid_codes = ['zh', 'en', 'ja', 'ko', 'es', 'fr', 'de']
    if lang_code not in valid_codes:
        raise ValidationError(
            message="Invalid language code",
            details={
                "language_code": lang_code,
                "valid_codes": valid_codes
            }
        )
    return lang_code
