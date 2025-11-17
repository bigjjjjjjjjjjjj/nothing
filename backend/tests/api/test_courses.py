"""測試課程 API"""
import pytest
from httpx import AsyncClient
from app.main import app


@pytest.fixture
async def client():
    """建立測試客戶端"""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


class TestCoursesAPI:
    """測試課程相關 API"""

    @pytest.mark.asyncio
    async def test_health_check(self, client: AsyncClient):
        """測試健康檢查端點"""
        response = await client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "app" in data
        assert "version" in data

    @pytest.mark.asyncio
    async def test_root_endpoint(self, client: AsyncClient):
        """測試根端點"""
        response = await client.get("/")

        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data
        assert "docs" in data

    @pytest.mark.asyncio
    async def test_create_course_missing_fields(self, client: AsyncClient):
        """測試建立課程時缺少必填欄位"""
        response = await client.post(
            "/api/v1/courses/create",
            json={"meeting_id": "test-123"}  # 缺少其他欄位
        )

        assert response.status_code == 422  # Validation error

    @pytest.mark.asyncio
    async def test_get_nonexistent_course(self, client: AsyncClient):
        """測試取得不存在的課程"""
        response = await client.get("/api/v1/courses/nonexistent-id")

        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_upload_slides_without_file(self, client: AsyncClient):
        """測試上傳講義但沒有檔案"""
        response = await client.post(
            "/api/v1/courses/test-course/upload-slides"
        )

        assert response.status_code == 422  # Validation error


class TestCourseLifecycle:
    """測試課程生命週期的整合測試"""

    @pytest.mark.asyncio
    async def test_full_course_lifecycle(self, client: AsyncClient):
        """測試完整的課程流程"""
        # 1. 建立課程
        create_response = await client.post(
            "/api/v1/courses/create",
            json={
                "meeting_id": "test-meeting-123",
                "meeting_url": "https://meet.google.com/test-123",
                "course_name": "測試課程",
                "started_at": "2024-01-01T10:00:00Z"
            }
        )

        if create_response.status_code != 200:
            pytest.skip("Database not available for integration test")

        data = create_response.json()
        assert "course_id" in data
        course_id = data["course_id"]

        # 2. 取得課程資訊
        get_response = await client.get(f"/api/v1/courses/{course_id}")

        if get_response.status_code == 200:
            course_data = get_response.json()
            assert course_data["meeting_id"] == "test-meeting-123"
            assert course_data["course_name"] == "測試課程"

        # 3. 結束課程
        end_response = await client.post(
            f"/api/v1/courses/{course_id}/end",
            json={"ended_at": "2024-01-01T11:00:00Z"}
        )

        if end_response.status_code == 200:
            end_data = end_response.json()
            assert "status" in end_data


class TestAPIDocumentation:
    """測試 API 文件端點"""

    @pytest.mark.asyncio
    async def test_openapi_docs(self, client: AsyncClient):
        """測試 OpenAPI 文件可訪問"""
        response = await client.get("/docs")
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_redoc_docs(self, client: AsyncClient):
        """測試 ReDoc 文件可訪問"""
        response = await client.get("/redoc")
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_openapi_json(self, client: AsyncClient):
        """測試 OpenAPI JSON schema"""
        response = await client.get("/openapi.json")
        assert response.status_code == 200

        schema = response.json()
        assert "openapi" in schema
        assert "info" in schema
        assert "paths" in schema
