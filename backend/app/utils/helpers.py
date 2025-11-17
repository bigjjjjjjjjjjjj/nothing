"""輔助工具函數"""
import hashlib
import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, Optional


def generate_id(prefix: str = "") -> str:
    """生成唯一 ID"""
    unique_id = str(uuid.uuid4())
    if prefix:
        return f"{prefix}_{unique_id}"
    return unique_id


def generate_course_id(meeting_id: str) -> str:
    """生成課程 ID"""
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    return f"course_{timestamp}_{meeting_id[:8]}"


def generate_quiz_id(course_id: str) -> str:
    """生成測驗 ID"""
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    return f"quiz_{timestamp}_{course_id[:8]}"


def hash_file_content(content: bytes) -> str:
    """計算檔案內容的 SHA256 雜湊值"""
    return hashlib.sha256(content).hexdigest()


def format_timestamp(dt: Optional[datetime] = None) -> str:
    """格式化時間戳記為 ISO 8601 格式"""
    if dt is None:
        dt = datetime.now()
    return dt.isoformat()


def parse_timestamp(timestamp_str: str) -> datetime:
    """解析 ISO 8601 時間戳記"""
    try:
        return datetime.fromisoformat(timestamp_str)
    except ValueError:
        # 嘗試其他常見格式
        formats = [
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%d",
            "%H:%M:%S",
        ]
        for fmt in formats:
            try:
                return datetime.strptime(timestamp_str, fmt)
            except ValueError:
                continue
        raise ValueError(f"Unable to parse timestamp: {timestamp_str}")


def format_duration(seconds: int) -> str:
    """格式化時長為人類可讀格式"""
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)

    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    else:
        return f"{minutes:02d}:{seconds:02d}"


def calculate_estimated_time(word_count: int, words_per_minute: int = 150) -> int:
    """計算預估閱讀/批改時間（秒）"""
    minutes = word_count / words_per_minute
    return int(minutes * 60)


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """截斷文字"""
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def merge_dicts(dict1: Dict[str, Any], dict2: Dict[str, Any]) -> Dict[str, Any]:
    """合併兩個字典（dict2 覆蓋 dict1）"""
    result = dict1.copy()
    result.update(dict2)
    return result


def batch_list(items: list, batch_size: int) -> list:
    """將列表分批"""
    return [items[i:i + batch_size] for i in range(0, len(items), batch_size)]


def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """安全除法（避免除以零）"""
    try:
        return numerator / denominator
    except ZeroDivisionError:
        return default


def percentage(part: float, total: float, decimals: int = 2) -> float:
    """計算百分比"""
    if total == 0:
        return 0.0
    return round((part / total) * 100, decimals)


def bytes_to_human_readable(bytes_size: int) -> str:
    """轉換位元組為人類可讀格式"""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_size < 1024.0:
            return f"{bytes_size:.2f} {unit}"
        bytes_size /= 1024.0
    return f"{bytes_size:.2f} PB"
