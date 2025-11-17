"""老師提示模型"""
from datetime import datetime
from sqlalchemy import Column, String, Integer, Text, Float, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
import enum

from app.core.database import Base


class HintType(str, enum.Enum):
    """提示類型枚舉"""
    EXAM = "exam"  # 會考試
    IMPORTANT = "important"  # 很重要
    ATTENTION = "attention"  # 要注意
    COMMON_MISTAKE = "common_mistake"  # 常見錯誤
    REMINDER = "reminder"  # 提醒複習


class TeacherHint(Base):
    """老師重點提示資料表"""
    __tablename__ = "teacher_hints"

    id = Column(Integer, primary_key=True, autoincrement=True)
    course_id = Column(String(50), ForeignKey("courses.id", ondelete="CASCADE"), nullable=False, index=True)
    timestamp = Column(String(20), nullable=False)  # HH:MM:SS
    hint_text = Column(Text, nullable=False)  # 老師說的原文
    hint_type = Column(String(20), nullable=False)  # exam, important, attention, etc.
    related_concept = Column(String(255))  # 相關概念
    slide_page = Column(Integer)  # 對應講義頁碼
    confidence = Column(Float)  # AI 識別的信心分數 (0-1)
    created_at = Column(DateTime, default=datetime.utcnow)

    # 關聯
    course = relationship("Course", back_populates="teacher_hints")

    # 建立複合索引
    __table_args__ = (
        Index('idx_teacher_hints_course_type', 'course_id', 'hint_type'),
    )

    def __repr__(self):
        return f"<TeacherHint {self.id}: {self.hint_type} at {self.timestamp}>"
