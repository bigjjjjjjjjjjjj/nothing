"""講義模型"""
from datetime import datetime
from sqlalchemy import Column, String, Integer, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from app.core.database import Base


class Slide(Base):
    """講義檔案資料表"""
    __tablename__ = "slides"

    id = Column(String(50), primary_key=True, index=True)
    course_id = Column(String(50), ForeignKey("courses.id", ondelete="CASCADE"), nullable=False, index=True)
    filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    total_pages = Column(Integer)
    extracted_text = Column(Text)
    uploaded_at = Column(DateTime, default=datetime.utcnow)

    # 關聯
    course = relationship("Course", back_populates="slides")

    def __repr__(self):
        return f"<Slide {self.id}: {self.filename}>"
