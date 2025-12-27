"""
Pytest Configuration and Fixtures.

This module contains shared fixtures and configuration for all tests.
"""

import asyncio
import os
from collections.abc import AsyncGenerator, Generator
from pathlib import Path
from typing import TYPE_CHECKING, Any

import pytest
import pytest_asyncio
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

if TYPE_CHECKING:
    from fastapi import FastAPI
    from httpx import AsyncClient

# Load test environment variables BEFORE importing app modules
_env_test_path = Path(__file__).parent.parent / ".env.test"
if _env_test_path.exists():
    load_dotenv(_env_test_path, override=False)  # Don't override CI env vars

# Set minimal required env vars for testing (only if not already set)
os.environ.setdefault(
    "SECRET_KEY", "test-secret-key-for-testing-purposes-only-min-32-chars"
)
os.environ.setdefault(
    "DATABASE_URL", "postgresql+asyncpg://postgres:postgres@localhost:5432/test_db"
)

from app.core.database import Base, get_db  # noqa: E402

# Test database URL (in-memory SQLite for tests)
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


# Import app only if it exists (for client fixture)
if TYPE_CHECKING:
    from fastapi import FastAPI


def _get_app() -> "FastAPI | None":
    """
    Try to import the FastAPI app.
    Returns None if app.main doesn't exist yet.
    """
    try:
        from app.main import app

        return app
    except (ImportError, ModuleNotFoundError):
        return None


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop]:
    """Create an instance of the event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="function")
async def async_engine():
    """Create a test database engine."""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=False,
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def async_session(async_engine) -> AsyncGenerator[AsyncSession]:
    """Create a test database session."""
    test_async_session_maker = async_sessionmaker(
        async_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
    )

    async with test_async_session_maker() as session:
        yield session


@pytest_asyncio.fixture(scope="function")
async def client(async_session: AsyncSession) -> AsyncGenerator["AsyncClient"]:
    """
    Create a test HTTP client with database session override.

    This fixture requires app.main to exist. It will skip tests
    that depend on it if the app module is not available.
    """
    from httpx import ASGITransport, AsyncClient

    app = _get_app()
    if app is None:
        pytest.skip("app.main module not available yet")

    async def override_get_db() -> AsyncGenerator[AsyncSession]:
        yield async_session

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest.fixture
def sample_user_data() -> dict[str, Any]:
    """Sample user data for testing."""
    return {
        "email": "test@example.com",
        "password": "SecurePassword123!",
        "first_name": "Test",
        "last_name": "User",
    }


@pytest.fixture
def sample_organization_data() -> dict[str, Any]:
    """Sample organization data for testing."""
    return {
        "name": "Test Church",
        "slug": "test-church",
    }


@pytest.fixture
def sample_department_data() -> dict[str, Any]:
    """Sample department data for testing."""
    return {
        "name": "Worship Team",
        "description": "Team responsible for worship services",
    }
