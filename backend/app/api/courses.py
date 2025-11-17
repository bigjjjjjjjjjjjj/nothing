"""課程相關 API"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
import uuid
from datetime import datetime

from app.core.database import get_db
from app.models.course import Course, CourseStatus
from app.models.slide import Slide
from app.schemas.course import (
    CourseCreate,
    CourseResponse,
    CourseAnalyzeRequest,
    CourseAnalyzeResponse,
)
from app.schemas.slide import SlideUploadResponse
from app.schemas.quiz import QuizScopeResponse, QuizScope
from app.services import course_service, slide_service, llm_service

router = APIRouter()


@router.post("/create", response_model=CourseResponse)
async def create_course(
    course_data: CourseCreate,
    db: AsyncSession = Depends(get_db)
):
    """建立新課程"""
    course_id = f"course_{uuid.uuid4().hex[:12]}"

    course = Course(
        id=course_id,
        user_id="default_user",  # TODO: 從認證系統取得
        meeting_id=course_data.meeting_id,
        meeting_url=course_data.meeting_url,
        course_name=course_data.course_name,
        started_at=course_data.started_at,
        status=CourseStatus.RECORDING,
    )

    db.add(course)
    await db.commit()
    await db.refresh(course)

    return CourseResponse(
        course_id=course.id,
        status=course.status.value,
        created_at=course.created_at,
    )


@router.get("/{course_id}")
async def get_course(
    course_id: str,
    db: AsyncSession = Depends(get_db)
):
    """取得課程資訊"""
    result = await db.execute(
        select(Course).where(Course.id == course_id)
    )
    course = result.scalar_one_or_none()

    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    return {
        "id": course.id,
        "course_name": course.course_name,
        "meeting_id": course.meeting_id,
        "status": course.status.value,
        "started_at": course.started_at,
        "ended_at": course.ended_at,
    }


@router.post("/{course_id}/upload-slides", response_model=SlideUploadResponse)
async def upload_slides(
    course_id: str,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    """上傳講義"""
    # 驗證課程存在
    result = await db.execute(
        select(Course).where(Course.id == course_id)
    )
    course = result.scalar_one_or_none()

    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    # 處理檔案上傳
    file_id = f"file_{uuid.uuid4().hex[:12]}"

    # TODO: 實作檔案儲存和文字擷取
    # 這裡需要整合 slide_service 來處理 PDF/PPT/Word
    extracted_text = "Sample extracted text..."  # 暫時的示例文字
    pages = 10  # 暫時的示例頁數

    slide = Slide(
        id=file_id,
        course_id=course_id,
        filename=file.filename,
        file_path=f"uploads/{file_id}_{file.filename}",
        total_pages=pages,
        extracted_text=extracted_text,
    )

    db.add(slide)
    await db.commit()

    return SlideUploadResponse(
        file_id=file_id,
        filename=file.filename,
        pages=pages,
        extracted_text_preview=extracted_text[:200],
        status="processed",
    )


@router.post("/{course_id}/analyze", response_model=CourseAnalyzeResponse)
async def analyze_course(
    course_id: str,
    request: CourseAnalyzeRequest,
    db: AsyncSession = Depends(get_db)
):
    """分析課程內容並生成重點"""
    # 驗證課程存在
    result = await db.execute(
        select(Course).where(Course.id == course_id)
    )
    course = result.scalar_one_or_none()

    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    # TODO: 整合 LLM 服務進行分析
    # 這裡需要呼叫 course_service.analyze_course()

    # 暫時回傳示例數據
    summary = {
        "key_points": [
            {
                "title": "二元樹定義",
                "content": "每個節點最多有兩個子節點",
                "slide_page": 3,
                "transcript_timestamps": ["00:05:23"],
            }
        ],
        "concepts": ["二元樹", "走訪"],
        "formulas": ["T(n) = 2T(n/2) + O(1)"],
    }

    return CourseAnalyzeResponse(
        summary=summary,
        status="completed",
    )


@router.post("/{course_id}/suggest-quiz-scopes", response_model=QuizScopeResponse)
async def suggest_quiz_scopes(
    course_id: str,
    db: AsyncSession = Depends(get_db)
):
    """建議題目生成範圍"""
    # 驗證課程存在
    result = await db.execute(
        select(Course).where(Course.id == course_id)
    )
    course = result.scalar_one_or_none()

    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    # TODO: 整合 LLM 服務分析範圍
    # 這裡需要呼叫 llm_service.suggest_scopes()

    # 暫時回傳示例數據
    suggested_scopes = [
        QuizScope(
            scope_id="scope_1",
            label="整堂課程",
            description="涵蓋本次課程所有內容",
            estimated_questions=15,
            coverage="all",
        ),
        QuizScope(
            scope_id="scope_2",
            label="3.1 二元樹的定義",
            description="包含二元樹定義、性質、表示法",
            slide_pages=[3, 4, 5],
            transcript_timestamps=["00:05:23", "00:08:45"],
            estimated_questions=8,
            coverage="section",
        ),
    ]

    return QuizScopeResponse(
        suggested_scopes=suggested_scopes,
        default_scope="scope_1",
        recommendation="建議先複習「老師說會考的部分」",
    )
