"""題庫模型"""
from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from app.core.database import Base


class Quiz(Base):
    """題庫資料表"""
    __tablename__ = "quizzes"

    id = Column(String(50), primary_key=True, index=True)
    course_id = Column(String(50), ForeignKey("courses.id", ondelete="CASCADE"), nullable=False, index=True)
    scope_id = Column(String(50))
    questions_json = Column(JSONB, nullable=False)  # 題目列表
    created_at = Column(DateTime, default=datetime.utcnow)

    # 關聯
    course = relationship("Course", back_populates="quizzes")
    submissions = relationship("QuizSubmission", back_populates="quiz", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Quiz {self.id} for course {self.course_id}>"


class QuizSubmission(Base):
    """作答紀錄資料表"""
    __tablename__ = "quiz_submissions"

    id = Column(String(50), primary_key=True, index=True)
    quiz_id = Column(String(50), ForeignKey("quizzes.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(String(50), nullable=False, index=True)
    answers_json = Column(JSONB, nullable=False)
    results_json = Column(JSONB)  # 批改結果
    score = Column(Integer)
    submitted_at = Column(DateTime, default=datetime.utcnow)

    # 關聯
    quiz = relationship("Quiz", back_populates="submissions")

    def __repr__(self):
        return f"<QuizSubmission {self.id} for quiz {self.quiz_id}>"
