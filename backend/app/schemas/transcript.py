"""轉錄相關 Schemas"""
from typing import List
from pydantic import BaseModel


class TranscriptItem(BaseModel):
    """轉錄項目"""
    timestamp: str
    text: str
    confidence: float
    is_final: bool = True


class TranscriptResponse(BaseModel):
    """轉錄響應"""
    type: str = "transcript"
    timestamp: str
    text: str
    confidence: float
    is_final: bool
