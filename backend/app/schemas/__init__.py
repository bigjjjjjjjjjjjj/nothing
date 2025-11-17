"""Pydantic Schemas"""
from .course import (
    CourseCreate,
    CourseResponse,
    CourseAnalyzeRequest,
    CourseAnalyzeResponse,
)
from .slide import SlideUploadResponse
from .transcript import TranscriptItem, TranscriptResponse
from .quiz import (
    QuizScopeResponse,
    QuizGenerateRequest,
    QuizGenerateResponse,
    QuizSubmitRequest,
    QuizSubmitResponse,
    QuizResultResponse,
)
from .teacher_hint import TeacherHintResponse, TeacherHintsListResponse

__all__ = [
    "CourseCreate",
    "CourseResponse",
    "CourseAnalyzeRequest",
    "CourseAnalyzeResponse",
    "SlideUploadResponse",
    "TranscriptItem",
    "TranscriptResponse",
    "QuizScopeResponse",
    "QuizGenerateRequest",
    "QuizGenerateResponse",
    "QuizSubmitRequest",
    "QuizSubmitResponse",
    "QuizResultResponse",
    "TeacherHintResponse",
    "TeacherHintsListResponse",
]
