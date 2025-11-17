"""老師提示識別服務"""
import re
import logging
from typing import Optional, Dict
from app.services.llm_service import llm_service, LLMServiceError

logger = logging.getLogger(__name__)


class HintService:
    """老師提示識別服務"""

    # 提示語關鍵字模式
    HINT_PATTERNS = {
        'exam': [
            '會考', '考試', '期中考', '期末考', '考試重點', '必考',
            '一定會考', '這個會考', '考試會出'
        ],
        'important': [
            '很重要', '重點', '一定要', '關鍵', '核心',
            '特別重要', '非常重要', '務必', '千萬'
        ],
        'attention': [
            '注意', '小心', '要特別', '留意', '記住',
            '要注意', '特別注意', '請注意'
        ],
        'common_mistake': [
            '常錯', '常犯', '容易錯', '大家都', '注意不要',
            '常見錯誤', '容易搞錯', '不要搞混'
        ],
        'reminder': [
            '記得', '要複習', '回去看', '下次',
            '記得要', '別忘了', '要記住'
        ]
    }

    def detect_hint(self, text: str) -> Optional[str]:
        """
        檢測文字中是否包含提示語

        Args:
            text: 要檢測的文字

        Returns:
            提示類型（exam/important/attention/common_mistake/reminder）或 None
        """
        for hint_type, patterns in self.HINT_PATTERNS.items():
            for pattern in patterns:
                if pattern in text:
                    return hint_type
        return None

    async def analyze_hint(
        self,
        hint_text: str,
        timestamp: str,
        context: str = ""
    ) -> Dict:
        """
        使用 LLM 分析提示內容

        Args:
            hint_text: 提示文字
            timestamp: 時間戳記
            context: 上下文（可選）

        Returns:
            分析結果，包含概念、頁碼、信心分數
        """
        try:
            prompt = f"""
分析以下老師的提示語，識別相關概念。

提示語：{hint_text}
時間點：{timestamp}
{f"上下文：{context}" if context else ""}

請簡短回答（不超過50字）：
1. 這個提示與哪個概念相關？
2. 信心分數（0-1）

請以簡短的 JSON 格式回傳：
{{"concept": "概念名稱", "confidence": 0.9}}
"""

            response = await llm_service.generate_completion(
                prompt,
                temperature=0.3,
                max_tokens=100
            )

            # 嘗試解析 JSON
            import json
            try:
                # 嘗試直接解析
                result = json.loads(response)
            except json.JSONDecodeError:
                # 嘗試提取 JSON 部分
                json_start = response.find('{')
                json_end = response.rfind('}') + 1
                if json_start != -1 and json_end > json_start:
                    result = json.loads(response[json_start:json_end])
                else:
                    # 如果解析失敗，使用預設值
                    result = {
                        "concept": "未知概念",
                        "confidence": 0.5
                    }

            return {
                "concept": result.get("concept", "未知概念"),
                "slide_page": result.get("slide_page"),
                "confidence": result.get("confidence", 0.5)
            }

        except Exception as e:
            logger.error(f"提示分析失敗: {str(e)}")
            # 返回預設值
            return {
                "concept": "未知概念",
                "slide_page": None,
                "confidence": 0.3
            }

    def extract_keywords(self, text: str) -> list:
        """提取文字中的關鍵字"""
        # 移除常見的停用詞
        stopwords = {'的', '是', '在', '有', '和', '這', '那', '要', '會', '了', '我', '你', '他'}

        # 簡單的分詞（實際應用中應該使用 jieba 等工具）
        words = re.findall(r'[\u4e00-\u9fff]+', text)

        # 過濾停用詞和短詞
        keywords = [w for w in words if len(w) > 1 and w not in stopwords]

        return list(set(keywords))[:5]  # 返回前5個不重複的關鍵字


# 建立全域實例
hint_service = HintService()
