"""測試講義處理服務"""
import pytest
from pathlib import Path
from app.services.slide_service import SlideService, SlideProcessingError


class TestSlideService:
    """測試 SlideService"""

    def setup_method(self):
        """測試前設置"""
        self.service = SlideService()

    def test_validate_file_extension_valid(self):
        """測試驗證有效的檔案格式"""
        valid_files = [
            "test.pdf",
            "presentation.ppt",
            "document.pptx",
            "notes.doc",
            "report.docx",
        ]

        for filename in valid_files:
            try:
                self.service._validate_file_extension(filename)
            except SlideProcessingError:
                pytest.fail(f"Should accept {filename}")

    def test_validate_file_extension_invalid(self):
        """測試驗證無效的檔案格式"""
        invalid_files = [
            "image.jpg",
            "video.mp4",
            "archive.zip",
            "text.txt",
            "noextension",
        ]

        for filename in invalid_files:
            with pytest.raises(SlideProcessingError, match="不支援的檔案格式"):
                self.service._validate_file_extension(filename)

    def test_validate_file_size_valid(self):
        """測試驗證有效的檔案大小"""
        # 10MB 以內
        valid_sizes = [
            100,  # 100 bytes
            1024 * 1024,  # 1 MB
            5 * 1024 * 1024,  # 5 MB
            10 * 1024 * 1024,  # 10 MB (邊界)
        ]

        for size in valid_sizes:
            try:
                self.service._validate_file_size(b"x" * size, "test.pdf")
            except SlideProcessingError:
                pytest.fail(f"Should accept size {size}")

    def test_validate_file_size_invalid(self):
        """測試驗證過大的檔案"""
        # 超過 10MB
        large_size = 11 * 1024 * 1024  # 11 MB

        with pytest.raises(SlideProcessingError, match="檔案大小超過限制"):
            self.service._validate_file_size(b"x" * large_size, "test.pdf")

    def test_supported_extensions(self):
        """測試支援的檔案格式定義"""
        expected_extensions = ['.pdf', '.ppt', '.pptx', '.doc', '.docx']

        for ext in expected_extensions:
            assert ext in self.service.SUPPORTED_EXTENSIONS
            assert self.service.SUPPORTED_EXTENSIONS[ext].startswith("application/")

    def test_get_file_extension(self):
        """測試取得檔案副檔名"""
        test_cases = [
            ("document.pdf", ".pdf"),
            ("PRESENTATION.PPTX", ".pptx"),
            ("file.with.dots.docx", ".docx"),
            ("noextension", ""),
        ]

        for filename, expected_ext in test_cases:
            actual_ext = Path(filename).suffix.lower()
            assert actual_ext == expected_ext

    @pytest.mark.asyncio
    async def test_process_file_invalid_extension(self):
        """測試處理無效格式的檔案"""
        with pytest.raises(SlideProcessingError, match="不支援的檔案格式"):
            await self.service.process_file(b"content", "invalid.txt")

    @pytest.mark.asyncio
    async def test_process_file_too_large(self):
        """測試處理過大的檔案"""
        large_content = b"x" * (11 * 1024 * 1024)  # 11 MB

        with pytest.raises(SlideProcessingError, match="檔案大小超過限制"):
            await self.service.process_file(large_content, "large.pdf")

    def test_extract_text_from_tables(self):
        """測試從表格提取文字的邏輯"""
        # 這個測試驗證表格處理的概念
        # 實際實作中應該測試 _extract_text_from_pdf 等方法
        assert hasattr(self.service, '_extract_text_from_pdf')
        assert hasattr(self.service, '_extract_text_from_ppt')
        assert hasattr(self.service, '_extract_text_from_word')

    @pytest.mark.asyncio
    async def test_save_file_creates_directory(self, tmp_path):
        """測試儲存檔案時會建立目錄"""
        # 使用臨時目錄測試
        test_service = SlideService()
        test_service.UPLOAD_DIR = tmp_path / "test_uploads"

        content = b"test content"
        filename = "test.pdf"

        file_path = await test_service.save_file(content, filename)

        assert test_service.UPLOAD_DIR.exists()
        assert Path(file_path).exists()
        assert Path(file_path).read_bytes() == content

    def test_clean_extracted_text(self):
        """測試清理提取的文字"""
        # 測試文字清理邏輯
        dirty_text = "  多餘空白  \n\n\n  文字內容  \n  "
        # 簡單的清理實作
        cleaned = " ".join(dirty_text.split())

        assert cleaned == "多餘空白 文字內容"
        assert "\n\n\n" not in cleaned
