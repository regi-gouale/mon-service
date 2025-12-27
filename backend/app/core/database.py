"""
Database Configuration.

This module contains SQLAlchemy 2.0 async engine and session management
with PostgreSQL via asyncpg driver.

Usage:
    from app.core.database import get_db, AsyncSessionLocal

    # As FastAPI dependency
    @app.get("/items")
    async def get_items(db: AsyncSession = Depends(get_db)):
        result = await db.execute(select(Item))
        return result.scalars().all()

    # As context manager for transactions
    async with transaction_context() as session:
        session.add(item)
        # Auto-commits on success, rollbacks on exception
"""

from collections.abc import AsyncGenerator
from contextlib import AbstractAsyncContextManager, asynccontextmanager

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings


class Base(DeclarativeBase):
    """
    Base class for all SQLAlchemy models.

    All database models should inherit from this class.
    It provides common functionality like metadata management
    and table creation.

    Example:
        class User(Base):
            __tablename__ = "users"
            id: Mapped[UUID] = mapped_column(primary_key=True)
            email: Mapped[str] = mapped_column(unique=True)
    """

    pass


def create_engine() -> AsyncEngine:
    """
    Create and configure the async SQLAlchemy engine.

    Returns:
        AsyncEngine: Configured async engine with connection pooling.

    Configuration:
        - Uses postgresql+asyncpg driver for async PostgreSQL support
        - pool_size: Number of connections to maintain (from settings)
        - max_overflow: Additional connections above pool_size (from settings)
        - pool_pre_ping: Tests connections before use for disconnect detection
        - pool_recycle: Recycles connections after 1 hour to prevent stale connections
        - echo: SQL logging enabled based on settings (typically for development)
    """
    return create_async_engine(
        str(settings.database_url),
        echo=settings.database_echo,
        pool_size=settings.database_pool_size,
        max_overflow=settings.database_max_overflow,
        pool_pre_ping=True,  # Pessimistic disconnect handling
        pool_recycle=3600,  # Recycle connections after 1 hour
    )


# Create async engine instance
engine: AsyncEngine = create_engine()

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# Alias for backward compatibility
async_session_maker = AsyncSessionLocal


async def get_db() -> AsyncGenerator[AsyncSession]:
    """
    FastAPI dependency for getting async database sessions.

    This is the primary way to get a database session in route handlers.
    The session is automatically closed after the request completes.
    Transactions are NOT auto-committed; you must explicitly commit.

    Yields:
        AsyncSession: An async database session.

    Example:
        @app.post("/users")
        async def create_user(
            user: UserCreate,
            db: AsyncSession = Depends(get_db)
        ):
            db_user = User(**user.model_dump())
            db.add(db_user)
            await db.commit()
            await db.refresh(db_user)
            return db_user
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


# Alias for backward compatibility
get_async_session = get_db


@asynccontextmanager
async def transaction_context() -> AsyncGenerator[AsyncSession]:
    """
    Context manager for database transactions with auto-commit/rollback.

    Use this for standalone operations outside of FastAPI request context,
    such as background tasks, CLI commands, or tests.

    The transaction is automatically committed on successful completion
    and rolled back if an exception occurs.

    Yields:
        AsyncSession: An async database session within a transaction.

    Example:
        async with transaction_context() as session:
            user = User(email="test@example.com")
            session.add(user)
            # Auto-commits here if no exception

    Raises:
        Exception: Re-raises any exception after rolling back the transaction.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


def get_transaction_context() -> AbstractAsyncContextManager[AsyncSession]:
    """
    Factory function for transaction context.

    Returns:
        AsyncContextManager[AsyncSession]: A context manager for transactions.

    This is useful when you need to pass the context manager as a parameter
    or when testing with dependency injection.
    """
    return transaction_context()


async def init_db() -> None:
    """
    Initialize database tables from models.

    Creates all tables defined in the Base metadata.
    Use this for development/testing. For production, use Alembic migrations.

    Warning:
        This does not update existing tables. Use Alembic for schema changes.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def drop_db() -> None:
    """
    Drop all database tables.

    Warning:
        This permanently deletes all data. Use only in development/testing.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


async def close_db() -> None:
    """
    Close database connections and dispose of the engine.

    Call this during application shutdown to properly clean up
    all connections in the pool.
    """
    await engine.dispose()
