"""轉錄相關 API (WebSocket)"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.ext.asyncio import AsyncSession
import json

from app.core.database import get_db
from app.schemas.transcript import TranscriptResponse

router = APIRouter()


@router.websocket("/ws/{course_id}")
async def websocket_transcribe(
    websocket: WebSocket,
    course_id: str,
):
    """WebSocket 即時語音轉錄"""
    await websocket.accept()

    try:
        print(f"WebSocket connected for course: {course_id}")

        while True:
            # 接收音訊資料 (binary)
            audio_data = await websocket.receive_bytes()

            # TODO: 整合語音辨識服務
            # 1. 呼叫 Google Speech-to-Text 或 Whisper
            # 2. 取得轉錄結果
            # 3. 儲存到資料庫
            # 4. 檢查是否包含老師提示語

            # 暫時回傳示例數據
            response = TranscriptResponse(
                type="transcript",
                timestamp="00:05:23",
                text="今天我們要講的是二元樹的走訪方法",
                confidence=0.92,
                is_final=True,
            )

            await websocket.send_json(response.dict())

    except WebSocketDisconnect:
        print(f"WebSocket disconnected for course: {course_id}")
    except Exception as e:
        print(f"WebSocket error: {e}")
        await websocket.close()
