"""題目相關 API"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import uuid
from datetime import datetime

from app.core.database import get_db
from app.models.quiz import Quiz, QuizSubmission
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

router = APIRouter()


@router.post("/generate", response_model=QuizGenerateResponse)
async def generate_quiz(
    request: QuizGenerateRequest,
    db: AsyncSession = Depends(get_db)
):
    """生成題目"""
    quiz_id = f"quiz_{uuid.uuid4().hex[:12]}"

    # TODO: 整合 LLM 服務生成題目
    # 這裡需要呼叫 llm_service.generate_questions()

    # 暫時回傳示例數據
    questions = [
        {
            "question_id": "q1",
            "type": "multiple_choice",
            "question_text": "以下何者是二元樹的特性？",
            "options": [
                "每個節點最多有兩個子節點",
                "每個節點必須有兩個子節點",
                "每個節點最多有一個子節點",
                "節點數量必須是偶數",
            ],
            "correct_answer": "每個節點最多有兩個子節點",
            "explanation": "二元樹的定義是每個節點最多有兩個子節點",
            "slide_reference": 3,
            "video_timestamp": "00:05:23",
            "difficulty": "easy",
        }
    ]

    quiz = Quiz(
        id=quiz_id,
        course_id=request.course_id,
        scope_id=request.scope_id,
        questions_json=questions,
    )

    db.add(quiz)
    await db.commit()

    return QuizGenerateResponse(
        quiz_id=quiz_id,
        questions=[Question(**q) for q in questions],
        created_at=datetime.utcnow().isoformat(),
    )


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
