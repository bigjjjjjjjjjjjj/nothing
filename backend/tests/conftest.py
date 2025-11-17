"""Pytest 配置和共用 fixtures"""
import pytest
import asyncio
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from app.core.database import Base
from app.core.config import settings

# 測試資料庫 URL
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(scope="session")
def event_loop():
    """建立事件循環"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
async def test_db() -> AsyncGenerator[AsyncSession, None]:
    """建立測試資料庫 session"""
    # 建立測試引擎
    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
        future=True,
    )

    # 建立所有表
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # 建立 session maker
    async_session = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    # 提供 session
    async with async_session() as session:
        yield session

    # 清理
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest.fixture
def sample_course_data():
    """範例課程資料"""
    return {
        "meeting_id": "test-meeting-123",
        "meeting_url": "https://meet.google.com/test-123",
        "course_name": "測試課程",
        "started_at": "2024-01-01T10:00:00Z",
    }


@pytest.fixture
def sample_transcript_text():
    """範例轉錄文字"""
    return """
    今天我們要講解二次方程式。
    二次方程式的一般形式是 ax² + bx + c = 0。
    這個會考，大家要特別注意。
    解二次方程式有三種方法：因式分解、配方法、和公式解。
    """


@pytest.fixture
def sample_slide_text():
    """範例講義文字"""
    return """
    第一章：二次方程式

    1. 定義
       二次方程式是形如 ax² + bx + c = 0 的方程式
       其中 a ≠ 0

    2. 解法
       - 因式分解
       - 配方法
       - 公式解：x = (-b ± √(b²-4ac)) / 2a

    3. 判別式
       Δ = b² - 4ac
       Δ > 0：兩相異實根
       Δ = 0：重根
       Δ < 0：兩共軛複根
    """
