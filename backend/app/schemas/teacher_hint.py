"""老師提示相關 Schemas"""
from typing import List, Dict, Optional
from pydantic import BaseModel


class TeacherHintResponse(BaseModel):
    """老師提示響應"""
    id: int
    timestamp: str
    hint_text: str
    hint_type: str
    related_concept: Optional[str] = None
    slide_page: Optional[int] = None
    confidence: float
    video_url: Optional[str] = None


class TeacherHintsListResponse(BaseModel):
    """老師提示列表響應"""
    hints: List[TeacherHintResponse]
    total: int
    by_type: Dict[str, int]
