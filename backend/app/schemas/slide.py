"""講義相關 Schemas"""
from pydantic import BaseModel


class SlideUploadResponse(BaseModel):
    """講義上傳響應"""
    file_id: str
    filename: str
    pages: int
    extracted_text_preview: str
    status: str = "processed"
