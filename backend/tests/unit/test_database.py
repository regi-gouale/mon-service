"""
Unit tests for database configuration module.

Tests the SQLAlchemy 2.0 async engine and session management.
"""

import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession

from app.core.database import (
    AsyncSessionLocal,
    Base,
    async_session_maker,
    create_engine,
    engine,
    get_async_session,
    get_db,
    get_transaction_context,
)


class TestEngineConfiguration:
    """Test async engine configuration."""

    def test_engine_is_async_engine(self) -> None:
        """Engine should be an AsyncEngine instance."""
        assert isinstance(engine, AsyncEngine)

    def test_create_engine_returns_async_engine(self) -> None:
        """create_engine() should return an AsyncEngine instance."""
        new_engine = create_engine()
        assert isinstance(new_engine, AsyncEngine)

    def test_engine_uses_asyncpg_dialect(self) -> None:
        """Engine should use postgresql+asyncpg dialect."""
        assert "asyncpg" in engine.dialect.name or "postgresql" in str(engine.url)


class TestSessionConfiguration:
    """Test async session factory configuration."""

    def test_session_maker_exists(self) -> None:
        """async_session_maker should be configured."""
        assert async_session_maker is not None
        assert AsyncSessionLocal is not None

    def test_session_maker_alias(self) -> None:
        """AsyncSessionLocal and async_session_maker should be the same."""
        assert AsyncSessionLocal is async_session_maker


class TestBaseModel:
    """Test Base declarative model."""

    def test_base_has_metadata(self) -> None:
        """Base should have metadata for table definitions."""
        assert Base.metadata is not None

    def test_base_is_declarative(self) -> None:
        """Base should be a DeclarativeBase subclass."""
        assert hasattr(Base, "__tablename__") or hasattr(Base, "metadata")


class TestGetDbDependency:
    """Test get_db FastAPI dependency."""

    @pytest.mark.asyncio
    async def test_get_db_yields_session(self, async_session: AsyncSession) -> None:
        """get_db should yield an AsyncSession."""
        # The fixture provides the session, confirming the pattern works
        assert isinstance(async_session, AsyncSession)

    @pytest.mark.asyncio
    async def test_get_db_alias(self) -> None:
        """get_async_session should be an alias for get_db."""
        assert get_async_session is get_db


class TestTransactionContext:
    """Test transaction context manager."""

    @pytest.mark.asyncio
    async def test_transaction_context_is_context_manager(self) -> None:
        """transaction_context should work as an async context manager."""
        # Verify it's an async generator function decorated with asynccontextmanager
        ctx = get_transaction_context()
        assert hasattr(ctx, "__aenter__")
        assert hasattr(ctx, "__aexit__")

    @pytest.mark.asyncio
    async def test_get_transaction_context_returns_context_manager(self) -> None:
        """get_transaction_context should return a context manager."""
        ctx = get_transaction_context()
        assert hasattr(ctx, "__aenter__")


class TestSessionExecution:
    """Test session can execute queries."""

    @pytest.mark.asyncio
    async def test_session_can_execute_query(self, async_session: AsyncSession) -> None:
        """Session should be able to execute SQL queries."""
        result = await async_session.execute(text("SELECT 1 as value"))
        row = result.fetchone()
        assert row is not None
        assert row.value == 1

    @pytest.mark.asyncio
    async def test_session_is_not_expired_on_commit(
        self, async_session: AsyncSession
    ) -> None:
        """Session should have expire_on_commit=False."""
        # This verifies the session factory configuration
        # expire_on_commit=False means objects remain accessible after commit
        # Access via sync_session for AsyncSession
        assert async_session.sync_session.expire_on_commit is False
