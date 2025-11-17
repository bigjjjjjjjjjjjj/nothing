"""轉錄相關 API (WebSocket)"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta
import logging
import asyncio

from app.core.database import AsyncSessionLocal
from app.models.transcript import Transcript
from app.models.teacher_hint import TeacherHint
from app.schemas.transcript import TranscriptResponse
from app.services.speech_service import speech_service, SpeechServiceError
from app.services.hint_service import hint_service

logger = logging.getLogger(__name__)
router = APIRouter()


@router.websocket("/ws/{course_id}")
async def websocket_transcribe(
    websocket: WebSocket,
    course_id: str,
):
    """WebSocket 即時語音轉錄"""
    await websocket.accept()

    if not speech_service:
        await websocket.send_json({
            "type": "error",
            "message": "語音辨識服務未初始化"
        })
        await websocket.close()
        return

    start_time = datetime.now()
    logger.info(f"WebSocket connected for course: {course_id}")

    try:
        # 建立音訊串流生成器
        async def audio_stream_generator():
            while True:
                try:
                    audio_data = await websocket.receive_bytes()
                    yield audio_data
                except WebSocketDisconnect:
                    break

        # 處理語音辨識結果
        async for result in speech_service.recognize_stream(audio_stream_generator()):
            # 計算時間戳記
            elapsed = datetime.now() - start_time
            timestamp = str(timedelta(seconds=int(elapsed.total_seconds())))

            # 準備回應
            response_data = {
                "type": "transcript",
                "timestamp": timestamp,
                "text": result["text"],
                "confidence": result["confidence"],
                "is_final": result["is_final"],
            }

            # 如果是最終結果，儲存到資料庫
            if result["is_final"]:
                async with AsyncSessionLocal() as db:
                    try:
                        # 儲存轉錄
                        transcript = Transcript(
                            course_id=course_id,
                            timestamp=timestamp,
                            text=result["text"],
                            confidence=result["confidence"],
                        )
                        db.add(transcript)

                        # 檢查是否包含老師提示語
                        hint_type = hint_service.detect_hint(result["text"])
                        if hint_type:
                            logger.info(f"檢測到提示語: {hint_type}")

                            # 分析提示內容
                            hint_analysis = await hint_service.analyze_hint(
                                result["text"],
                                timestamp
                            )

                            # 儲存老師提示
                            teacher_hint = TeacherHint(
                                course_id=course_id,
                                timestamp=timestamp,
                                hint_text=result["text"],
                                hint_type=hint_type,
                                related_concept=hint_analysis["concept"],
                                slide_page=hint_analysis.get("slide_page"),
                                confidence=hint_analysis["confidence"],
                            )
                            db.add(teacher_hint)

                            # 發送提示通知
                            await websocket.send_json({
                                "type": "teacher_hint",
                                "timestamp": timestamp,
                                "hint_type": hint_type,
                                "text": result["text"],
                            })

                        await db.commit()

                    except Exception as e:
                        logger.error(f"資料庫操作失敗: {str(e)}")
                        await db.rollback()

            # 發送轉錄結果
            await websocket.send_json(response_data)

    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for course: {course_id}")
    except SpeechServiceError as e:
        logger.error(f"語音辨識錯誤: {str(e)}")
        await websocket.send_json({
            "type": "error",
            "message": f"語音辨識失敗: {str(e)}"
        })
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}")
        await websocket.send_json({
            "type": "error",
            "message": f"系統錯誤: {str(e)}"
        })
    finally:
        await websocket.close()
