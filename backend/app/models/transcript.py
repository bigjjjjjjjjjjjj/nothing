"""語音轉錄模型"""
from datetime import datetime
from sqlalchemy import Column, String, Integer, Text, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from app.core.database import Base


class Transcript(Base):
    """語音轉錄資料表"""
    __tablename__ = "transcripts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    course_id = Column(String(50), ForeignKey("courses.id", ondelete="CASCADE"), nullable=False, index=True)
    timestamp = Column(String(20), nullable=False)  # HH:MM:SS 格式
    text = Column(Text, nullable=False)
    confidence = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)

    # 關聯
    course = relationship("Course", back_populates="transcripts")

    def __repr__(self):
        return f"<Transcript {self.id}: {self.timestamp}>"
