"""題目相關 API"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import uuid
from datetime import datetime

from app.core.database import get_db
from app.models.quiz import Quiz, QuizSubmission
from app.models.course import Course
from app.models.slide import Slide
from app.models.transcript import Transcript
from app.schemas.quiz import (
    QuizGenerateRequest,
    QuizGenerateResponse,
    QuizSubmitRequest,
    QuizSubmitResponse,
    QuizResultResponse,
    Question,
    QuizResult,
    RecommendedReview,
)
from app.services.llm_service import llm_service, LLMServiceError

router = APIRouter()


@router.post("/generate", response_model=QuizGenerateResponse)
async def generate_quiz(
    request: QuizGenerateRequest,
    db: AsyncSession = Depends(get_db)
):
    """生成題目"""
    # 驗證課程存在
    course_result = await db.execute(
        select(Course).where(Course.id == request.course_id)
    )
    course = course_result.scalar_one_or_none()

    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    try:
        # 取得講義內容
        slides_result = await db.execute(
            select(Slide).where(Slide.course_id == request.course_id)
        )
        slides = slides_result.scalars().all()
        slides_text = "\n\n".join([slide.extracted_text for slide in slides if slide.extracted_text])

        # 取得語音轉錄
        transcript_result = await db.execute(
            select(Transcript).where(Transcript.course_id == request.course_id).order_by(Transcript.timestamp)
        )
        transcripts = transcript_result.scalars().all()
        transcript_text = "\n".join([f"[{t.timestamp}] {t.text}" for t in transcripts])

        # 合併內容
        content = f"{slides_text}\n\n{transcript_text}"

        if not content.strip():
            raise HTTPException(
                status_code=400,
                detail="沒有可用的內容，請先上傳講義或進行轉錄"
            )

        # 轉換題型格式
        question_types = {
            'multiple_choice': request.question_types.multiple_choice,
            'fill_in_blank': request.question_types.fill_in_blank,
            'short_answer': request.question_types.short_answer,
        }

        # 使用 LLM 生成題目
        questions_data = await llm_service.generate_questions(
            content,
            question_types,
            request.difficulty
        )

        # 儲存題目
        quiz_id = f"quiz_{uuid.uuid4().hex[:12]}"
        quiz = Quiz(
            id=quiz_id,
            course_id=request.course_id,
            scope_id=request.scope_id,
            questions_json=questions_data,
        )

        db.add(quiz)
        await db.commit()
        await db.refresh(quiz)

        return QuizGenerateResponse(
            quiz_id=quiz_id,
            questions=[Question(**q) for q in questions_data],
            created_at=datetime.utcnow().isoformat(),
        )

    except LLMServiceError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"題目生成失敗: {str(e)}")


@router.post("/{quiz_id}/submit", response_model=QuizSubmitResponse)
async def submit_quiz(
    quiz_id: str,
    request: QuizSubmitRequest,
    db: AsyncSession = Depends(get_db)
):
    """提交答案"""
    # 驗證題目存在
    result = await db.execute(
        select(Quiz).where(Quiz.id == quiz_id)
    )
    quiz = result.scalar_one_or_none()

    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")

    submission_id = f"sub_{uuid.uuid4().hex[:12]}"

    # 儲存提交記錄
    submission = QuizSubmission(
        id=submission_id,
        quiz_id=quiz_id,
        user_id="default_user",  # TODO: 從認證系統取得
        answers_json=[answer.dict() for answer in request.answers],
    )

    db.add(submission)
    await db.commit()

    # TODO: 背景任務批改（使用 Celery）
    # 這裡應該觸發批改任務

    return QuizSubmitResponse(
        submission_id=submission_id,
        status="grading",
        estimated_time="5 seconds",
    )


@router.get("/{quiz_id}/result", response_model=QuizResultResponse)
async def get_quiz_result(
    quiz_id: str,
    submission_id: str,
    db: AsyncSession = Depends(get_db)
):
    """取得批改結果"""
    # 查詢提交記錄
    result = await db.execute(
        select(QuizSubmission).where(
            QuizSubmission.id == submission_id,
            QuizSubmission.quiz_id == quiz_id,
        )
    )
    submission = result.scalar_one_or_none()

    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")

    # TODO: 如果還在批改中，回傳狀態
    # 這裡應該檢查批改任務狀態

    # 暫時回傳示例數據
    results = [
        QuizResult(
            question_id="q1",
            is_correct=True,
            user_answer="每個節點最多有兩個子節點",
            feedback="正確！",
        )
    ]

    return QuizResultResponse(
        quiz_id=quiz_id,
        submission_id=submission_id,
        total_questions=1,
        correct_count=1,
        score=100,
        results=results,
        weak_concepts=[],
        recommended_review=RecommendedReview(
            slide_pages=[],
            video_timestamps=[],
        ),
    )
