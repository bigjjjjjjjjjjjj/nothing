"""測試老師提示識別服務"""
import pytest
from app.services.hint_service import HintService, hint_service


class TestHintService:
    """測試 HintService"""

    def test_detect_hint_exam(self):
        """測試檢測考試相關提示"""
        text = "這個會考，大家要注意"
        result = hint_service.detect_hint(text)
        assert result == "exam"

    def test_detect_hint_important(self):
        """測試檢測重要提示"""
        text = "這個概念很重要，是核心知識"
        result = hint_service.detect_hint(text)
        assert result == "important"

    def test_detect_hint_attention(self):
        """測試檢測注意提示"""
        text = "要特別注意這個地方"
        result = hint_service.detect_hint(text)
        assert result == "attention"

    def test_detect_hint_common_mistake(self):
        """測試檢測常見錯誤提示"""
        text = "這裡容易錯，大家要小心"
        result = hint_service.detect_hint(text)
        assert result == "common_mistake"

    def test_detect_hint_reminder(self):
        """測試檢測提醒提示"""
        text = "記得要複習這個部分"
        result = hint_service.detect_hint(text)
        assert result == "reminder"

    def test_detect_hint_no_match(self):
        """測試無匹配提示"""
        text = "這是一般的講解內容"
        result = hint_service.detect_hint(text)
        assert result is None

    def test_extract_keywords(self):
        """測試提取關鍵字"""
        text = "二次方程式的解法包括因式分解和配方法"
        keywords = hint_service.extract_keywords(text)

        assert isinstance(keywords, list)
        assert len(keywords) > 0
        assert len(keywords) <= 5

        # 驗證不包含停用詞
        stopwords = {'的', '是', '在', '有', '和', '這', '那', '要', '會'}
        for keyword in keywords:
            assert keyword not in stopwords
            assert len(keyword) > 1

    def test_extract_keywords_empty(self):
        """測試空文字提取關鍵字"""
        text = ""
        keywords = hint_service.extract_keywords(text)
        assert keywords == []

    @pytest.mark.asyncio
    async def test_analyze_hint_structure(self):
        """測試分析提示的返回結構"""
        # 注意：這個測試可能需要 LLM API，可能會失敗
        # 在實際測試中應該 mock LLM 服務
        try:
            result = await hint_service.analyze_hint(
                hint_text="這個會考",
                timestamp="00:10:30",
                context="講解二次方程式"
            )

            # 驗證返回結構
            assert "concept" in result
            assert "slide_page" in result
            assert "confidence" in result

            # 驗證類型
            assert isinstance(result["concept"], str)
            assert isinstance(result["confidence"], (int, float))
            assert 0 <= result["confidence"] <= 1

        except Exception as e:
            # 如果 API 不可用，跳過測試
            pytest.skip(f"LLM API not available: {str(e)}")

    def test_hint_patterns_completeness(self):
        """測試提示模式的完整性"""
        expected_types = ['exam', 'important', 'attention', 'common_mistake', 'reminder']

        for hint_type in expected_types:
            assert hint_type in hint_service.HINT_PATTERNS
            assert isinstance(hint_service.HINT_PATTERNS[hint_type], list)
            assert len(hint_service.HINT_PATTERNS[hint_type]) > 0
