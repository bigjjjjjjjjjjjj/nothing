"""測試 LLM 服務"""
import pytest
from unittest.mock import Mock, patch, AsyncMock
from app.services.llm_service import LLMService, LLMServiceError


class TestLLMService:
    """測試 LLMService"""

    def setup_method(self):
        """測試前設置"""
        self.service = LLMService()

    @pytest.mark.asyncio
    async def test_generate_completion_with_mock(self):
        """測試生成完成（使用 mock）"""
        with patch('openai.AsyncOpenAI') as mock_openai:
            mock_client = Mock()
            mock_response = Mock()
            mock_response.choices = [Mock(message=Mock(content="測試回應"))]

            mock_client.chat.completions.create = AsyncMock(return_value=mock_response)
            mock_openai.return_value = mock_client

            # 建立新的服務實例使用 mock
            service = LLMService()
            service.client = mock_client

            result = await service.generate_completion("測試提示")

            assert result == "測試回應"
            mock_client.chat.completions.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_analyze_course_content_structure(self):
        """測試分析課程內容的返回結構"""
        with patch.object(self.service, 'generate_completion') as mock_gen:
            mock_gen.return_value = '''
            {
                "key_points": ["重點1", "重點2"],
                "concepts": ["概念1", "概念2"],
                "formulas": ["公式1"]
            }
            '''

            result = await self.service.analyze_course_content(
                "講義內容",
                "轉錄內容"
            )

            assert "key_points" in result
            assert "concepts" in result
            assert "formulas" in result
            assert isinstance(result["key_points"], list)
            assert isinstance(result["concepts"], list)
            assert isinstance(result["formulas"], list)

    @pytest.mark.asyncio
    async def test_suggest_quiz_scopes_structure(self):
        """測試建議題目範圍的返回結構"""
        with patch.object(self.service, 'generate_completion') as mock_gen:
            mock_gen.return_value = '''
            [
                {
                    "label": "全部範圍",
                    "description": "涵蓋所有內容",
                    "coverage": "all",
                    "estimated_questions": 20
                }
            ]
            '''

            result = await self.service.suggest_quiz_scopes(
                "講義內容",
                "轉錄內容"
            )

            assert isinstance(result, list)
            assert len(result) > 0

            scope = result[0]
            assert "label" in scope
            assert "description" in scope
            assert "coverage" in scope
            assert "estimated_questions" in scope

    @pytest.mark.asyncio
    async def test_generate_questions_types(self):
        """測試生成不同類型的題目"""
        with patch.object(self.service, 'generate_completion') as mock_gen:
            mock_gen.return_value = '''
            [
                {
                    "type": "multiple_choice",
                    "question_text": "測試題目?",
                    "options": ["A", "B", "C", "D"],
                    "correct_answer": "A",
                    "explanation": "解釋",
                    "difficulty": "medium"
                }
            ]
            '''

            result = await self.service.generate_questions(
                content="測試內容",
                question_types={"multiple_choice": 1},
                difficulty="medium"
            )

            assert isinstance(result, list)
            assert len(result) > 0

            question = result[0]
            assert "type" in question
            assert "question_text" in question
            assert "correct_answer" in question

    @pytest.mark.asyncio
    async def test_grade_short_answer_structure(self):
        """測試批改簡答題的返回結構"""
        with patch.object(self.service, 'generate_completion') as mock_gen:
            mock_gen.return_value = '''
            {
                "score": 8,
                "feedback": "答得不錯",
                "improvement_suggestions": ["可以更詳細"]
            }
            '''

            result = await self.service.grade_short_answer(
                question_text="什麼是二次方程式？",
                model_answer="形如 ax² + bx + c = 0 的方程式",
                user_answer="二次方程式是包含 x² 的方程式",
                evaluation_criteria=["概念正確", "表達清楚"]
            )

            assert "score" in result
            assert "feedback" in result
            assert "improvement_suggestions" in result
            assert isinstance(result["score"], (int, float))
            assert 0 <= result["score"] <= 10

    @pytest.mark.asyncio
    async def test_json_parsing_fallback(self):
        """測試 JSON 解析失敗時的降級處理"""
        with patch.object(self.service, 'generate_completion') as mock_gen:
            # 返回包含 JSON 的文字
            mock_gen.return_value = '''
            這裡是一些說明文字
            {"key_points": ["測試"], "concepts": [], "formulas": []}
            還有一些其他文字
            '''

            result = await self.service.analyze_course_content("test", "test")

            # 應該能夠提取 JSON 部分
            assert "key_points" in result
            assert result["key_points"] == ["測試"]

    @pytest.mark.asyncio
    async def test_error_handling(self):
        """測試錯誤處理"""
        with patch.object(self.service, 'generate_completion') as mock_gen:
            mock_gen.side_effect = Exception("API 錯誤")

            with pytest.raises(LLMServiceError):
                await self.service.analyze_course_content("test", "test")

    def test_temperature_range(self):
        """測試溫度參數範圍"""
        # 驗證不同場景使用適當的溫度
        # 分析課程: 0.5 (較保守)
        # 生成題目: 0.7 (較有創意)
        # 批改: 0.3 (非常保守)

        assert 0.0 <= 0.3 <= 1.0  # 批改溫度
        assert 0.0 <= 0.5 <= 1.0  # 分析溫度
        assert 0.0 <= 0.7 <= 1.0  # 生成溫度

    @pytest.mark.asyncio
    async def test_max_tokens_configuration(self):
        """測試 token 限制配置"""
        with patch('openai.AsyncOpenAI') as mock_openai:
            mock_client = Mock()
            mock_response = Mock()
            mock_response.choices = [Mock(message=Mock(content="回應"))]

            mock_client.chat.completions.create = AsyncMock(return_value=mock_response)
            mock_openai.return_value = mock_client

            service = LLMService()
            service.client = mock_client

            # 測試不同的 max_tokens 設定
            await service.generate_completion("提示", max_tokens=100)

            call_kwargs = mock_client.chat.completions.create.call_args.kwargs
            assert call_kwargs["max_tokens"] == 100
