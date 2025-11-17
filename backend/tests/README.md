# CourseAI 測試套件

本目錄包含 CourseAI 後端的測試套件。

## 測試結構

```
tests/
├── conftest.py           # Pytest 配置和共用 fixtures
├── services/             # 服務層測試
│   ├── test_hint_service.py
│   ├── test_llm_service.py
│   └── test_slide_service.py
└── api/                  # API 層測試
    └── test_courses.py
```

## 執行測試

### 執行所有測試
```bash
cd backend
pytest
```

### 執行特定測試文件
```bash
pytest tests/services/test_hint_service.py
```

### 執行特定測試類別
```bash
pytest tests/services/test_hint_service.py::TestHintService
```

### 執行特定測試函數
```bash
pytest tests/services/test_hint_service.py::TestHintService::test_detect_hint_exam
```

### 查看詳細輸出
```bash
pytest -v
```

### 查看覆蓋率
```bash
pytest --cov=app --cov-report=html
```

### 執行特定標記的測試
```bash
# 只執行單元測試
pytest -m unit

# 只執行整合測試
pytest -m integration

# 排除需要 API 的測試
pytest -m "not requires_api"
```

## 測試類型

### 單元測試 (Unit Tests)
測試單一功能或類別，不依賴外部服務。

位置：`tests/services/`

範例：
- `test_hint_service.py`：測試提示檢測邏輯
- `test_slide_service.py`：測試檔案驗證邏輯

### 整合測試 (Integration Tests)
測試多個元件的整合，可能需要資料庫或外部服務。

位置：`tests/api/`

範例：
- `test_courses.py`：測試 API 端點和完整流程

## 測試資料

測試使用的範例資料定義在 `conftest.py` 的 fixtures 中：

- `sample_course_data`：範例課程資料
- `sample_transcript_text`：範例轉錄文字
- `sample_slide_text`：範例講義文字
- `test_db`：測試資料庫 session

## Mock 和 Fixtures

### Mock 外部服務
對於依賴外部 API 的測試（如 OpenAI），使用 `unittest.mock` 進行 mock：

```python
from unittest.mock import patch, AsyncMock

@pytest.mark.asyncio
async def test_with_mock():
    with patch('openai.AsyncOpenAI') as mock_openai:
        # 設定 mock 行為
        mock_client = Mock()
        mock_openai.return_value = mock_client

        # 執行測試
        result = await service.method()
```

### 使用 Fixtures
在 `conftest.py` 中定義的 fixtures 可以在任何測試中使用：

```python
def test_example(sample_course_data):
    # 使用 fixture 提供的資料
    assert sample_course_data["meeting_id"] == "test-meeting-123"
```

## 最佳實踐

1. 每個測試應該獨立，不依賴其他測試的執行順序
2. 使用描述性的測試名稱，清楚表達測試意圖
3. 測試應該快速執行，避免不必要的延遲
4. 對於需要外部服務的測試，使用 mock 或標記為 `requires_api`
5. 保持測試簡潔，一個測試只驗證一個行為
6. 使用 fixtures 避免重複的設定代碼

## 持續整合

在 CI/CD 流程中，建議：
1. 每次提交都執行快速的單元測試
2. 每次合併前執行完整的測試套件
3. 定期執行需要外部服務的整合測試
4. 監控測試覆蓋率，維持在 80% 以上

## 故障排除

### 測試失敗：資料庫連線錯誤
確保已設定測試資料庫環境變數或使用記憶體資料庫（sqlite）。

### 測試失敗：API 不可用
對於標記為 `requires_api` 的測試，確保已配置 API 金鑰。
或使用 `pytest -m "not requires_api"` 跳過這些測試。

### 測試執行緩慢
使用 `pytest-xdist` 平行執行測試：
```bash
pip install pytest-xdist
pytest -n auto
```
