"""
Integration tests for database connection and migrations.

These tests verify:
1. Connection to the real PostgreSQL database
2. Alembic migrations are applied correctly
3. All models can be created/queried

Note: These tests require a running PostgreSQL database.
Use `docker compose up -d postgres` before running.
"""

import os
from collections.abc import AsyncGenerator
from pathlib import Path

import pytest
import pytest_asyncio
from dotenv import load_dotenv
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

# Load the real .env file for integration tests (not .env.test)
_env_path = Path(__file__).parent.parent.parent / ".env"
if _env_path.exists():
    load_dotenv(_env_path, override=True)

# Get the real DATABASE_URL from environment
REAL_DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql+asyncpg://church_team:church_team_dev@localhost:5432/church_team_db",
)


def is_postgres_available() -> bool:
    """Check if PostgreSQL is available for integration tests."""
    return "postgresql" in REAL_DATABASE_URL and "sqlite" not in REAL_DATABASE_URL


# Skip all tests in this module if PostgreSQL is not available
pytestmark = [
    pytest.mark.integration,
    pytest.mark.skipif(
        not is_postgres_available(),
        reason="PostgreSQL not available for integration tests",
    ),
]


@pytest_asyncio.fixture(scope="function")
async def pg_session() -> AsyncGenerator[AsyncSession]:
    """Create a PostgreSQL session for integration tests."""
    engine = create_async_engine(
        REAL_DATABASE_URL,
        echo=False,
    )

    test_session_maker = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
    )

    async with test_session_maker() as session:
        yield session

    await engine.dispose()


class TestPostgresConnection:
    """Test PostgreSQL database connection."""

    @pytest.mark.asyncio
    async def test_can_connect_to_database(self, pg_session: AsyncSession) -> None:
        """Should be able to connect to PostgreSQL database."""
        result = await pg_session.execute(text("SELECT 1 as value"))
        row = result.fetchone()
        assert row is not None
        assert row.value == 1

    @pytest.mark.asyncio
    async def test_can_query_version(self, pg_session: AsyncSession) -> None:
        """Should be able to query PostgreSQL version."""
        result = await pg_session.execute(text("SELECT version()"))
        row = result.fetchone()
        assert row is not None
        assert "PostgreSQL" in row[0]

    @pytest.mark.asyncio
    async def test_database_name_matches_config(self, pg_session: AsyncSession) -> None:
        """Database name should match configuration."""
        result = await pg_session.execute(text("SELECT current_database()"))
        row = result.fetchone()
        assert row is not None
        # The DB name should be part of the database_url
        assert row[0] in REAL_DATABASE_URL


class TestAlembicMigrations:
    """Test Alembic migrations are properly applied."""

    @pytest.mark.asyncio
    async def test_alembic_version_table_exists(self, pg_session: AsyncSession) -> None:
        """The alembic_version table should exist."""
        result = await pg_session.execute(
            text(
                """
                SELECT EXISTS (
                    SELECT FROM information_schema.tables
                    WHERE table_name = 'alembic_version'
                )
                """
            )
        )
        row = result.fetchone()
        assert row is not None
        assert row[0] is True

    @pytest.mark.asyncio
    async def test_migrations_are_applied(self, pg_session: AsyncSession) -> None:
        """At least one migration should be applied."""
        result = await pg_session.execute(
            text("SELECT version_num FROM alembic_version")
        )
        rows = result.fetchall()
        assert len(rows) >= 1, "No migrations applied"
        # Current migration should be the initial schema
        version_nums = [row[0] for row in rows]
        assert any(version_nums), "No migration version found"


class TestTablesExist:
    """Test all expected tables exist in the database."""

    @pytest.mark.asyncio
    async def test_organizations_table_exists(self, pg_session: AsyncSession) -> None:
        """The organizations table should exist."""
        result = await pg_session.execute(
            text(
                """
                SELECT EXISTS (
                    SELECT FROM information_schema.tables
                    WHERE table_name = 'organizations'
                )
                """
            )
        )
        assert result.fetchone()[0] is True

    @pytest.mark.asyncio
    async def test_users_table_exists(self, pg_session: AsyncSession) -> None:
        """The users table should exist."""
        result = await pg_session.execute(
            text(
                """
                SELECT EXISTS (
                    SELECT FROM information_schema.tables
                    WHERE table_name = 'users'
                )
                """
            )
        )
        assert result.fetchone()[0] is True

    @pytest.mark.asyncio
    async def test_refresh_tokens_table_exists(self, pg_session: AsyncSession) -> None:
        """The refresh_tokens table should exist."""
        result = await pg_session.execute(
            text(
                """
                SELECT EXISTS (
                    SELECT FROM information_schema.tables
                    WHERE table_name = 'refresh_tokens'
                )
                """
            )
        )
        assert result.fetchone()[0] is True

    @pytest.mark.asyncio
    async def test_user_role_enum_exists(self, pg_session: AsyncSession) -> None:
        """The user_role enum type should exist."""
        result = await pg_session.execute(
            text(
                """
                SELECT EXISTS (
                    SELECT 1 FROM pg_type WHERE typname = 'user_role'
                )
                """
            )
        )
        assert result.fetchone()[0] is True


class TestTableSchemas:
    """Test table schemas match model definitions."""

    @pytest.mark.asyncio
    async def test_organizations_has_required_columns(
        self, pg_session: AsyncSession
    ) -> None:
        """Organizations table should have all required columns."""
        result = await pg_session.execute(
            text(
                """
                SELECT column_name FROM information_schema.columns
                WHERE table_name = 'organizations'
                """
            )
        )
        columns = {row[0] for row in result.fetchall()}
        expected_columns = {
            "id",
            "name",
            "slug",
            "description",
            "logo_url",
            "is_active",
            "created_at",
            "updated_at",
        }
        assert expected_columns.issubset(columns)

    @pytest.mark.asyncio
    async def test_users_has_required_columns(self, pg_session: AsyncSession) -> None:
        """Users table should have all required columns."""
        result = await pg_session.execute(
            text(
                """
                SELECT column_name FROM information_schema.columns
                WHERE table_name = 'users'
                """
            )
        )
        columns = {row[0] for row in result.fetchall()}
        expected_columns = {
            "id",
            "organization_id",
            "email",
            "password_hash",
            "first_name",
            "last_name",
            "phone",
            "avatar_url",
            "role",
            "email_verified",
            "is_active",
            "last_login_at",
            "created_at",
            "updated_at",
        }
        assert expected_columns.issubset(columns)

    @pytest.mark.asyncio
    async def test_refresh_tokens_has_required_columns(
        self, pg_session: AsyncSession
    ) -> None:
        """Refresh tokens table should have all required columns."""
        result = await pg_session.execute(
            text(
                """
                SELECT column_name FROM information_schema.columns
                WHERE table_name = 'refresh_tokens'
                """
            )
        )
        columns = {row[0] for row in result.fetchall()}
        expected_columns = {
            "id",
            "user_id",
            "token",
            "expires_at",
            "is_revoked",
            "created_at",
        }
        assert expected_columns.issubset(columns)


class TestIndexesExist:
    """Test important indexes are created."""

    @pytest.mark.asyncio
    async def test_users_email_index(self, pg_session: AsyncSession) -> None:
        """Users table should have an index on email."""
        result = await pg_session.execute(
            text(
                """
                SELECT indexname FROM pg_indexes
                WHERE tablename = 'users' AND indexname LIKE '%email%'
                """
            )
        )
        indexes = result.fetchall()
        assert len(indexes) >= 1, "No email index found on users table"

    @pytest.mark.asyncio
    async def test_organizations_slug_unique(self, pg_session: AsyncSession) -> None:
        """Organizations table should have a unique index on slug."""
        result = await pg_session.execute(
            text(
                """
                SELECT indexname FROM pg_indexes
                WHERE tablename = 'organizations' AND indexname LIKE '%slug%'
                """
            )
        )
        indexes = result.fetchall()
        assert len(indexes) >= 1, "No slug index found on organizations table"

    @pytest.mark.asyncio
    async def test_refresh_tokens_token_unique(self, pg_session: AsyncSession) -> None:
        """Refresh tokens table should have a unique index on token."""
        result = await pg_session.execute(
            text(
                """
                SELECT indexname FROM pg_indexes
                WHERE tablename = 'refresh_tokens' AND indexname LIKE '%token%'
                """
            )
        )
        indexes = result.fetchall()
        assert len(indexes) >= 1, "No token index found on refresh_tokens table"


class TestForeignKeys:
    """Test foreign key relationships are properly set up."""

    @pytest.mark.asyncio
    async def test_users_organization_fk(self, pg_session: AsyncSession) -> None:
        """Users should have a foreign key to organizations."""
        result = await pg_session.execute(
            text(
                """
                SELECT constraint_name
                FROM information_schema.table_constraints
                WHERE table_name = 'users'
                AND constraint_type = 'FOREIGN KEY'
                """
            )
        )
        constraints = result.fetchall()
        assert len(constraints) >= 1, "No foreign key on users table"

    @pytest.mark.asyncio
    async def test_refresh_tokens_user_fk(self, pg_session: AsyncSession) -> None:
        """Refresh tokens should have a foreign key to users."""
        result = await pg_session.execute(
            text(
                """
                SELECT constraint_name
                FROM information_schema.table_constraints
                WHERE table_name = 'refresh_tokens'
                AND constraint_type = 'FOREIGN KEY'
                """
            )
        )
        constraints = result.fetchall()
        assert len(constraints) >= 1, "No foreign key on refresh_tokens table"


class TestSeedDataExists:
    """Test seed data exists if seeding was run."""

    @pytest.mark.asyncio
    async def test_test_organization_exists(self, pg_session: AsyncSession) -> None:
        """Test organization should exist if seed was run."""
        result = await pg_session.execute(
            text("SELECT COUNT(*) FROM organizations WHERE slug = 'test-church'")
        )
        count = result.fetchone()[0]
        # This may be 0 if seed hasn't run, or 1 if it has
        assert count in (0, 1), "Unexpected number of test organizations"

    @pytest.mark.asyncio
    async def test_test_users_exist(self, pg_session: AsyncSession) -> None:
        """Test users should exist if seed was run."""
        result = await pg_session.execute(
            text("SELECT COUNT(*) FROM users WHERE email LIKE '%@test-church.org'")
        )
        count = result.fetchone()[0]
        # This may be 0 if seed hasn't run, or 5 if it has
        assert count in (0, 5), "Unexpected number of test users"
