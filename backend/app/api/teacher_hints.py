"""老師提示相關 API"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Optional

from app.core.database import get_db
from app.models.teacher_hint import TeacherHint
from app.schemas.teacher_hint import TeacherHintResponse, TeacherHintsListResponse

router = APIRouter()


@router.get("/{course_id}", response_model=TeacherHintsListResponse)
async def get_teacher_hints(
    course_id: str,
    hint_type: Optional[str] = Query(None, description="篩選類型: exam, important, etc."),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """取得老師重點提示列表"""
    # 建立查詢
    query = select(TeacherHint).where(TeacherHint.course_id == course_id)

    if hint_type:
        query = query.where(TeacherHint.hint_type == hint_type)

    query = query.order_by(TeacherHint.timestamp).limit(limit)

    # 執行查詢
    result = await db.execute(query)
    hints = result.scalars().all()

    # 統計各類型數量
    count_query = select(
        TeacherHint.hint_type,
        func.count(TeacherHint.id)
    ).where(
        TeacherHint.course_id == course_id
    ).group_by(TeacherHint.hint_type)

    count_result = await db.execute(count_query)
    by_type = {row[0]: row[1] for row in count_result}

    # 組裝響應
    hint_responses = [
        TeacherHintResponse(
            id=hint.id,
            timestamp=hint.timestamp,
            hint_text=hint.hint_text,
            hint_type=hint.hint_type,
            related_concept=hint.related_concept,
            slide_page=hint.slide_page,
            confidence=hint.confidence,
            video_url=f"https://drive.google.com/file/d/xxx?t={hint.timestamp}",  # TODO: 實際的影片URL
        )
        for hint in hints
    ]

    return TeacherHintsListResponse(
        hints=hint_responses,
        total=len(hints),
        by_type=by_type,
    )
