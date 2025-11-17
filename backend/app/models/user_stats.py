"""使用者統計模型"""
from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, DateTime
from sqlalchemy.dialects.postgresql import JSONB

from app.core.database import Base


class UserStats(Base):
    """使用者統計資料表"""
    __tablename__ = "user_stats"

    user_id = Column(String(50), primary_key=True, index=True)
    total_courses = Column(Integer, default=0)
    total_quizzes_taken = Column(Integer, default=0)
    average_score = Column(Float, default=0.0)
    weak_concepts = Column(JSONB)  # 弱項概念列表
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<UserStats {self.user_id}: {self.total_courses} courses, avg {self.average_score}>"
