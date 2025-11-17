"""題目相關 Schemas"""
from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field


class QuizScope(BaseModel):
    """題目範圍"""
    scope_id: str
    label: str
    description: str
    slide_pages: Optional[List[int]] = None
    transcript_timestamps: Optional[List[str]] = None
    estimated_questions: int
    coverage: str = "section"  # all, section, subsection, important


class TeacherHintInScope(BaseModel):
    """範圍內的老師提示"""
    timestamp: str
    hint_text: str
    related_concept: str
    slide_page: Optional[int] = None


class QuizScopeResponse(BaseModel):
    """建議題目範圍響應"""
    suggested_scopes: List[QuizScope]
    default_scope: str
    recommendation: Optional[str] = None


class QuestionTypes(BaseModel):
    """題型數量"""
    multiple_choice: int = Field(default=0, ge=0)
    fill_in_blank: int = Field(default=0, ge=0)
    short_answer: int = Field(default=0, ge=0)


class QuizGenerateRequest(BaseModel):
    """生成題目請求"""
    course_id: str
    scope_id: str
    question_types: QuestionTypes
    difficulty: str = Field(default="medium", pattern="^(easy|medium|hard)$")


class Question(BaseModel):
    """題目"""
    question_id: str
    type: str  # multiple_choice, fill_in_blank, short_answer
    question_text: str
    options: Optional[List[str]] = None
    correct_answer: str
    explanation: str
    slide_reference: Optional[int] = None
    video_timestamp: Optional[str] = None
    difficulty: str


class QuizGenerateResponse(BaseModel):
    """生成題目響應"""
    quiz_id: str
    questions: List[Question]
    created_at: str


class Answer(BaseModel):
    """答案"""
    question_id: str
    user_answer: str


class QuizSubmitRequest(BaseModel):
    """提交答案請求"""
    answers: List[Answer]


class QuizSubmitResponse(BaseModel):
    """提交答案響應"""
    submission_id: str
    status: str = "grading"
    estimated_time: str = "5 seconds"


class QuizResult(BaseModel):
    """批改結果"""
    question_id: str
    is_correct: bool
    user_answer: str
    score: Optional[int] = None
    feedback: str
    improvement_suggestions: Optional[List[str]] = None


class RecommendedReview(BaseModel):
    """推薦複習內容"""
    slide_pages: List[int]
    video_timestamps: List[str]


class QuizResultResponse(BaseModel):
    """批改結果響應"""
    quiz_id: str
    submission_id: str
    total_questions: int
    correct_count: int
    score: int
    results: List[QuizResult]
    weak_concepts: List[str]
    recommended_review: RecommendedReview
