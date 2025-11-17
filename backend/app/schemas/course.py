"""課程相關 Schemas"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class CourseCreate(BaseModel):
    """建立課程請求"""
    meeting_id: str = Field(..., description="Google Meet 會議 ID")
    meeting_url: str = Field(..., description="會議 URL")
    course_name: str = Field(..., description="課程名稱")
    started_at: datetime = Field(..., description="開始時間")


class CourseResponse(BaseModel):
    """課程響應"""
    course_id: str
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


class KeyPoint(BaseModel):
    """重點項目"""
    title: str
    content: str
    slide_page: Optional[int] = None
    transcript_timestamps: List[str] = []


class CourseSummary(BaseModel):
    """課程摘要"""
    key_points: List[KeyPoint]
    concepts: List[str]
    formulas: List[str]


class CourseAnalyzeRequest(BaseModel):
    """分析課程內容請求"""
    include_slides: bool = Field(default=True, description="是否包含講義")
    include_transcript: bool = Field(default=True, description="是否包含轉錄")


class CourseAnalyzeResponse(BaseModel):
    """分析課程內容響應"""
    summary: CourseSummary
    status: str = "completed"
