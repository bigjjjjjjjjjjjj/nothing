"""課程摘要模型"""
from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from app.core.database import Base


class CourseSummary(Base):
    """課程摘要資料表"""
    __tablename__ = "course_summaries"

    id = Column(String(50), primary_key=True, index=True)
    course_id = Column(String(50), ForeignKey("courses.id", ondelete="CASCADE"), unique=True, nullable=False)
    summary_json = Column(JSONB, nullable=False)  # 包含 key_points, concepts, formulas
    created_at = Column(DateTime, default=datetime.utcnow)

    # 關聯
    course = relationship("Course", back_populates="summary")

    def __repr__(self):
        return f"<CourseSummary {self.id} for course {self.course_id}>"
