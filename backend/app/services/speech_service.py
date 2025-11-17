"""語音轉文字服務"""
import io
import logging
from typing import AsyncGenerator, Optional
from abc import ABC, abstractmethod

try:
    from google.cloud import speech_v1
    GOOGLE_SPEECH_AVAILABLE = True
except ImportError:
    GOOGLE_SPEECH_AVAILABLE = False

from app.core.config import settings

logger = logging.getLogger(__name__)


class SpeechServiceError(Exception):
    """語音轉文字錯誤"""
    pass


class SpeechRecognizer(ABC):
    """語音辨識基礎類"""

    @abstractmethod
    async def recognize_stream(
        self,
        audio_stream: AsyncGenerator[bytes, None],
        language_code: str = "zh-TW"
    ) -> AsyncGenerator[dict, None]:
        """串流語音辨識"""
        pass


class GoogleSpeechRecognizer(SpeechRecognizer):
    """Google Speech-to-Text 服務"""

    def __init__(self):
        if not GOOGLE_SPEECH_AVAILABLE:
            raise SpeechServiceError(
                "Google Speech SDK 未安裝。請執行: pip install google-cloud-speech"
            )

        if not settings.GOOGLE_APPLICATION_CREDENTIALS:
            logger.warning("GOOGLE_APPLICATION_CREDENTIALS 未設置，Google Speech 功能可能無法使用")

        self.client = speech_v1.SpeechClient()

    async def recognize_stream(
        self,
        audio_stream: AsyncGenerator[bytes, None],
        language_code: str = "zh-TW"
    ) -> AsyncGenerator[dict, None]:
        """串流語音辨識"""
        try:
            # 配置辨識設定
            config = speech_v1.RecognitionConfig(
                encoding=speech_v1.RecognitionConfig.AudioEncoding.LINEAR16,
                sample_rate_hertz=16000,
                language_code=language_code,
                enable_automatic_punctuation=True,
                model="latest_long",
            )

            streaming_config = speech_v1.StreamingRecognitionConfig(
                config=config,
                interim_results=True,
            )

            # 建立請求生成器
            async def request_generator():
                yield speech_v1.StreamingRecognizeRequest(
                    streaming_config=streaming_config
                )
                async for audio_chunk in audio_stream:
                    yield speech_v1.StreamingRecognizeRequest(
                        audio_content=audio_chunk
                    )

            # 執行辨識
            responses = self.client.streaming_recognize(request_generator())

            for response in responses:
                if not response.results:
                    continue

                result = response.results[0]
                if not result.alternatives:
                    continue

                alternative = result.alternatives[0]

                yield {
                    "text": alternative.transcript,
                    "confidence": alternative.confidence if result.is_final else 0.0,
                    "is_final": result.is_final,
                }

        except Exception as e:
            logger.error(f"Google Speech 辨識失敗: {str(e)}")
            raise SpeechServiceError(f"語音辨識失敗: {str(e)}")

    def recognize_file(self, audio_content: bytes, language_code: str = "zh-TW") -> str:
        """辨識音訊檔案"""
        try:
            audio = speech_v1.RecognitionAudio(content=audio_content)

            config = speech_v1.RecognitionConfig(
                encoding=speech_v1.RecognitionConfig.AudioEncoding.LINEAR16,
                sample_rate_hertz=16000,
                language_code=language_code,
                enable_automatic_punctuation=True,
            )

            response = self.client.recognize(config=config, audio=audio)

            transcript = ""
            for result in response.results:
                transcript += result.alternatives[0].transcript + " "

            return transcript.strip()

        except Exception as e:
            logger.error(f"檔案辨識失敗: {str(e)}")
            raise SpeechServiceError(f"語音辨識失敗: {str(e)}")


class WhisperRecognizer(SpeechRecognizer):
    """Whisper 本地語音辨識"""

    def __init__(self, model_name: str = "base"):
        try:
            import whisper
            self.model = whisper.load_model(model_name)
        except ImportError:
            raise SpeechServiceError(
                "Whisper 未安裝。請執行: pip install openai-whisper"
            )

    async def recognize_stream(
        self,
        audio_stream: AsyncGenerator[bytes, None],
        language_code: str = "zh"
    ) -> AsyncGenerator[dict, None]:
        """串流語音辨識（Whisper 不支援真正的串流，這裡使用分段處理）"""
        buffer = b""
        chunk_size = 16000 * 2 * 5  # 5 秒的音訊

        async for audio_chunk in audio_stream:
            buffer += audio_chunk

            # 當緩衝區達到一定大小時處理
            if len(buffer) >= chunk_size:
                text = await self._recognize_chunk(buffer[:chunk_size], language_code)
                buffer = buffer[chunk_size:]

                if text:
                    yield {
                        "text": text,
                        "confidence": 0.9,  # Whisper 不提供信心分數
                        "is_final": True,
                    }

        # 處理剩餘的音訊
        if buffer:
            text = await self._recognize_chunk(buffer, language_code)
            if text:
                yield {
                    "text": text,
                    "confidence": 0.9,
                    "is_final": True,
                }

    async def _recognize_chunk(self, audio_data: bytes, language: str) -> str:
        """辨識音訊片段"""
        try:
            import numpy as np
            import tempfile
            import soundfile as sf

            # 將 bytes 轉換為 numpy array
            audio_array = np.frombuffer(audio_data, dtype=np.int16).astype(np.float32) / 32768.0

            # 使用臨時文件
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
                sf.write(temp_file.name, audio_array, 16000)
                result = self.model.transcribe(
                    temp_file.name,
                    language=language,
                    fp16=False
                )

            return result["text"].strip()

        except Exception as e:
            logger.error(f"Whisper 辨識失敗: {str(e)}")
            return ""

    def recognize_file(self, audio_path: str, language: str = "zh") -> str:
        """辨識音訊檔案"""
        try:
            result = self.model.transcribe(audio_path, language=language)
            return result["text"].strip()
        except Exception as e:
            logger.error(f"Whisper 檔案辨識失敗: {str(e)}")
            raise SpeechServiceError(f"語音辨識失敗: {str(e)}")


class SpeechService:
    """語音轉文字服務管理器"""

    def __init__(self):
        self.recognizer: Optional[SpeechRecognizer] = None
        self._initialize_recognizer()

    def _initialize_recognizer(self):
        """初始化辨識器"""
        if settings.USE_GOOGLE_SPEECH and GOOGLE_SPEECH_AVAILABLE:
            try:
                self.recognizer = GoogleSpeechRecognizer()
                logger.info("使用 Google Speech-to-Text 服務")
            except Exception as e:
                logger.warning(f"Google Speech 初始化失敗: {str(e)}")

        if not self.recognizer:
            try:
                self.recognizer = WhisperRecognizer(settings.WHISPER_MODEL)
                logger.info(f"使用 Whisper 模型: {settings.WHISPER_MODEL}")
            except Exception as e:
                logger.error(f"Whisper 初始化失敗: {str(e)}")
                raise SpeechServiceError("無法初始化任何語音辨識服務")

    async def recognize_stream(
        self,
        audio_stream: AsyncGenerator[bytes, None],
        language_code: str = "zh-TW"
    ) -> AsyncGenerator[dict, None]:
        """串流語音辨識"""
        if not self.recognizer:
            raise SpeechServiceError("語音辨識服務未初始化")

        async for result in self.recognizer.recognize_stream(audio_stream, language_code):
            yield result

    def recognize_file(self, audio_content: bytes, language_code: str = "zh-TW") -> str:
        """辨識音訊檔案"""
        if not self.recognizer:
            raise SpeechServiceError("語音辨識服務未初始化")

        if isinstance(self.recognizer, GoogleSpeechRecognizer):
            return self.recognizer.recognize_file(audio_content, language_code)
        else:
            # Whisper 需要檔案路徑，這裡需要額外處理
            raise SpeechServiceError("Whisper 檔案辨識需要檔案路徑")


# 建立全域實例
try:
    speech_service = SpeechService()
except Exception as e:
    logger.error(f"語音服務初始化失敗: {str(e)}")
    speech_service = None
