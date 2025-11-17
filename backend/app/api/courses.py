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
from app.services.slide_service import slide_service, SlideProcessingError
from app.services.llm_service import llm_service, LLMServiceError
from app.models.transcript import Transcript

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

    # 檢查檔案格式
    if not slide_service.is_supported_file(file.filename):
        raise HTTPException(
            status_code=400,
            detail=f"不支援的檔案格式。支援格式: PDF, PPT, PPTX, DOC, DOCX"
        )

    try:
        # 讀取檔案內容
        file_content = await file.read()

        # 處理檔案並擷取文字
        processed_data = await slide_service.process_file(file_content, file.filename)

        # 儲存檔案到本地
        file_id = f"file_{uuid.uuid4().hex[:12]}"
        unique_filename = f"{file_id}_{file.filename}"
        file_path = await slide_service.save_file(file_content, unique_filename)

        # 儲存到資料庫
        slide = Slide(
            id=file_id,
            course_id=course_id,
            filename=file.filename,
            file_path=file_path,
            total_pages=processed_data['total_pages'],
            extracted_text=processed_data['extracted_text'],
        )

        db.add(slide)
        await db.commit()
        await db.refresh(slide)

        # 回傳結果
        return SlideUploadResponse(
            file_id=file_id,
            filename=file.filename,
            pages=processed_data['total_pages'],
            extracted_text_preview=processed_data['extracted_text'][:200],
            status="processed",
        )

    except SlideProcessingError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"檔案處理失敗: {str(e)}")


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

    try:
        # 取得講義內容
        slides_text = ""
        if request.include_slides:
            slides_result = await db.execute(
                select(Slide).where(Slide.course_id == course_id)
            )
            slides = slides_result.scalars().all()
            slides_text = "\n\n".join([slide.extracted_text for slide in slides if slide.extracted_text])

        # 取得語音轉錄
        transcript_text = ""
        if request.include_transcript:
            transcript_result = await db.execute(
                select(Transcript).where(Transcript.course_id == course_id).order_by(Transcript.timestamp)
            )
            transcripts = transcript_result.scalars().all()
            transcript_text = "\n".join([f"[{t.timestamp}] {t.text}" for t in transcripts])

        if not slides_text and not transcript_text:
            raise HTTPException(
                status_code=400,
                detail="沒有可分析的內容，請先上傳講義或進行轉錄"
            )

        # 使用 LLM 分析課程內容
        summary = await llm_service.analyze_course_content(slides_text, transcript_text)

        return CourseAnalyzeResponse(
            summary=summary,
            status="completed",
        )

    except LLMServiceError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"課程分析失敗: {str(e)}")


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

    try:
        # 取得講義內容
        slides_result = await db.execute(
            select(Slide).where(Slide.course_id == course_id)
        )
        slides = slides_result.scalars().all()
        slides_text = "\n\n".join([slide.extracted_text for slide in slides if slide.extracted_text])

        # 取得語音轉錄
        transcript_result = await db.execute(
            select(Transcript).where(Transcript.course_id == course_id).order_by(Transcript.timestamp)
        )
        transcripts = transcript_result.scalars().all()
        transcript_text = "\n".join([f"[{t.timestamp}] {t.text}" for t in transcripts])

        if not slides_text and not transcript_text:
            raise HTTPException(
                status_code=400,
                detail="沒有可分析的內容，請先上傳講義或進行轉錄"
            )

        # 使用 LLM 建議範圍
        scopes_data = await llm_service.suggest_quiz_scopes(slides_text, transcript_text)

        # 轉換為 QuizScope 物件
        suggested_scopes = [QuizScope(**scope) for scope in scopes_data]

        return QuizScopeResponse(
            suggested_scopes=suggested_scopes,
            default_scope=suggested_scopes[0].scopeId if suggested_scopes else "scope_1",
            recommendation="建議先複習重點範圍",
        )

    except LLMServiceError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"範圍建議失敗: {str(e)}")
