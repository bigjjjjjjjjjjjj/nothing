"""LLM 整合服務"""
import json
import logging
from typing import List, Dict, Any, Optional
from openai import AsyncOpenAI
from app.core.config import settings

logger = logging.getLogger(__name__)


class LLMServiceError(Exception):
    """LLM 服務錯誤"""
    pass


class LLMService:
    """LLM 整合服務（支援 OpenAI API）"""

    def __init__(self):
        if settings.OPENAI_API_KEY:
            self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        else:
            self.client = None
            logger.warning("OPENAI_API_KEY 未設置，LLM 功能將無法使用")

    async def generate_completion(
        self,
        prompt: str,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000,
    ) -> str:
        """生成文字補全"""
        if not self.client:
            raise LLMServiceError("LLM 服務未初始化，請檢查 API 金鑰設置")

        try:
            response = await self.client.chat.completions.create(
                model=model or settings.LLM_MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
                max_tokens=max_tokens,
            )

            return response.choices[0].message.content.strip()

        except Exception as e:
            logger.error(f"LLM 生成失敗: {str(e)}")
            raise LLMServiceError(f"LLM 生成失敗: {str(e)}")

    async def analyze_course_content(
        self,
        slides_text: str,
        transcript_text: str
    ) -> Dict[str, Any]:
        """分析課程內容並生成重點摘要"""
        prompt = f"""
分析以下課程內容，生成重點摘要。

講義內容：
{slides_text[:3000]}

課堂語音轉錄：
{transcript_text[:3000]}

請完成以下任務：
1. 提取 3-5 個核心重點，每個重點包含標題和詳細說明
2. 識別重要概念（關鍵詞）
3. 提取公式或重要定理

請以 JSON 格式回傳，格式如下：
{{
  "key_points": [
    {{
      "title": "重點標題",
      "content": "詳細說明",
      "slide_page": 頁碼或null,
      "transcript_timestamps": ["時間戳記"]
    }}
  ],
  "concepts": ["概念1", "概念2"],
  "formulas": ["公式1", "公式2"]
}}
"""

        try:
            response = await self.generate_completion(prompt, temperature=0.5)

            # 嘗試解析 JSON
            try:
                result = json.loads(response)
                return result
            except json.JSONDecodeError:
                # 如果回應不是有效的 JSON，嘗試提取 JSON 部分
                json_start = response.find('{')
                json_end = response.rfind('}') + 1
                if json_start != -1 and json_end > json_start:
                    result = json.loads(response[json_start:json_end])
                    return result
                else:
                    raise LLMServiceError("無法解析 LLM 回應")

        except Exception as e:
            logger.error(f"課程分析失敗: {str(e)}")
            raise LLMServiceError(f"課程分析失敗: {str(e)}")

    async def suggest_quiz_scopes(
        self,
        slides_text: str,
        transcript_text: str
    ) -> List[Dict[str, Any]]:
        """建議題目生成範圍"""
        prompt = f"""
分析以下課程內容，建議可以出題的範圍。

講義內容：
{slides_text[:2000]}

課堂語音轉錄：
{transcript_text[:2000]}

請識別：
1. 講義的章節結構（依據標題、編號）
2. 老師特別強調的內容
3. 每個範圍適合出幾題

請以 JSON 陣列格式回傳，格式如下：
[
  {{
    "scope_id": "scope_1",
    "label": "整堂課程",
    "description": "涵蓋本次課程所有內容",
    "estimated_questions": 15,
    "coverage": "all"
  }},
  {{
    "scope_id": "scope_2",
    "label": "章節名稱",
    "description": "章節說明",
    "slide_pages": [頁碼列表],
    "estimated_questions": 8,
    "coverage": "section"
  }}
]
"""

        try:
            response = await self.generate_completion(prompt, temperature=0.5)

            # 解析 JSON
            try:
                result = json.loads(response)
                return result
            except json.JSONDecodeError:
                # 嘗試提取 JSON 陣列
                json_start = response.find('[')
                json_end = response.rfind(']') + 1
                if json_start != -1 and json_end > json_start:
                    result = json.loads(response[json_start:json_end])
                    return result
                else:
                    raise LLMServiceError("無法解析 LLM 回應")

        except Exception as e:
            logger.error(f"範圍建議失敗: {str(e)}")
            raise LLMServiceError(f"範圍建議失敗: {str(e)}")

    async def generate_questions(
        self,
        content: str,
        question_types: Dict[str, int],
        difficulty: str = "medium"
    ) -> List[Dict[str, Any]]:
        """生成題目"""
        total_questions = sum(question_types.values())

        prompt = f"""
根據以下課程內容，生成 {total_questions} 題測驗題目。

課程內容：
{content[:3000]}

題型要求：
- 選擇題：{question_types.get('multiple_choice', 0)} 題
- 填充題：{question_types.get('fill_in_blank', 0)} 題
- 簡答題：{question_types.get('short_answer', 0)} 題

難度：{difficulty}

每題需包含：
1. 題目文字
2. 選項（選擇題）
3. 正確答案
4. 詳細解析

請以 JSON 陣列格式回傳，格式如下：
[
  {{
    "question_id": "q1",
    "type": "multiple_choice",
    "question_text": "題目文字",
    "options": ["選項A", "選項B", "選項C", "選項D"],
    "correct_answer": "選項A",
    "explanation": "詳細解析",
    "difficulty": "easy"
  }}
]
"""

        try:
            response = await self.generate_completion(
                prompt,
                temperature=0.7,
                max_tokens=3000
            )

            # 解析 JSON
            try:
                result = json.loads(response)
                return result
            except json.JSONDecodeError:
                json_start = response.find('[')
                json_end = response.rfind(']') + 1
                if json_start != -1 and json_end > json_start:
                    result = json.loads(response[json_start:json_end])
                    return result
                else:
                    raise LLMServiceError("無法解析 LLM 回應")

        except Exception as e:
            logger.error(f"題目生成失敗: {str(e)}")
            raise LLMServiceError(f"題目生成失敗: {str(e)}")

    async def grade_short_answer(
        self,
        question_text: str,
        model_answer: str,
        user_answer: str,
        evaluation_criteria: List[str]
    ) -> Dict[str, Any]:
        """批改簡答題"""
        prompt = f"""
請批改以下簡答題。

題目：{question_text}
標準答案：{model_answer}
評分標準：{', '.join(evaluation_criteria)}
學生答案：{user_answer}

請評估：
1. 答案是否涵蓋關鍵概念
2. 邏輯是否清晰
3. 是否有錯誤或不完整的地方

請以 JSON 格式回傳：
{{
  "score": 分數（0-100）,
  "feedback": "詳細回饋",
  "improvement_suggestions": ["改進建議1", "改進建議2"]
}}
"""

        try:
            response = await self.generate_completion(prompt, temperature=0.3)

            # 解析 JSON
            try:
                result = json.loads(response)
                return result
            except json.JSONDecodeError:
                json_start = response.find('{')
                json_end = response.rfind('}') + 1
                if json_start != -1 and json_end > json_start:
                    result = json.loads(response[json_start:json_end])
                    return result
                else:
                    raise LLMServiceError("無法解析 LLM 回應")

        except Exception as e:
            logger.error(f"簡答題批改失敗: {str(e)}")
            raise LLMServiceError(f"簡答題批改失敗: {str(e)}")


# 建立全域實例
llm_service = LLMService()
