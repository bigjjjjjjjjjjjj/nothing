"""課程模型"""
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Enum
from sqlalchemy.orm import relationship
import enum

from app.core.database import Base


class CourseStatus(str, enum.Enum):
    """課程狀態枚舉"""
    RECORDING = "recording"
    PROCESSING = "processing"
    COMPLETED = "completed"


class Course(Base):
    """課程資料表"""
    __tablename__ = "courses"

    id = Column(String(50), primary_key=True, index=True)
    user_id = Column(String(50), nullable=False, index=True)
    meeting_id = Column(String(100), unique=True, index=True)
    meeting_url = Column(String(255))
    course_name = Column(String(255))
    started_at = Column(DateTime)
    ended_at = Column(DateTime, nullable=True)
    status = Column(Enum(CourseStatus), default=CourseStatus.RECORDING)
    created_at = Column(DateTime, default=datetime.utcnow)

    # 關聯
    slides = relationship("Slide", back_populates="course", cascade="all, delete-orphan")
    transcripts = relationship("Transcript", back_populates="course", cascade="all, delete-orphan")
    summary = relationship("CourseSummary", back_populates="course", uselist=False, cascade="all, delete-orphan")
    quizzes = relationship("Quiz", back_populates="course", cascade="all, delete-orphan")
    teacher_hints = relationship("TeacherHint", back_populates="course", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Course {self.id}: {self.course_name}>"
