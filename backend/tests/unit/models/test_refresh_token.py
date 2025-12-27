"""
Tests for RefreshToken model.

This module contains tests for the RefreshToken SQLAlchemy model,
covering creation, properties, and relationships.
"""

from datetime import UTC, datetime, timedelta
from uuid import uuid4

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Organization, RefreshToken, User


class TestRefreshTokenModel:
    """Tests for RefreshToken model structure."""

    def test_refresh_token_creation_with_defaults(self) -> None:
        """Test creating a RefreshToken with required fields only.

        Note: SQLAlchemy defaults (like is_revoked=False) are only applied
        during INSERT, not at object instantiation. The default value
        is tested in the database tests.
        """
        user_id = str(uuid4())
        token = "test_token_value_123"
        expires_at = datetime.now(UTC) + timedelta(days=7)

        refresh_token = RefreshToken(
            user_id=user_id,
            token=token,
            expires_at=expires_at,
        )

        assert refresh_token.user_id == user_id
        assert refresh_token.token == token
        assert refresh_token.expires_at == expires_at
        # Note: is_revoked will be None until saved to DB where server_default applies

    def test_refresh_token_creation_with_all_fields(self) -> None:
        """Test creating a RefreshToken with all fields specified."""
        token_id = str(uuid4())
        user_id = str(uuid4())
        token = "full_token_value_456"
        expires_at = datetime.now(UTC) + timedelta(days=30)
        created_at = datetime.now(UTC)

        refresh_token = RefreshToken(
            id=token_id,
            user_id=user_id,
            token=token,
            expires_at=expires_at,
            is_revoked=True,
            created_at=created_at,
        )

        assert refresh_token.id == token_id
        assert refresh_token.user_id == user_id
        assert refresh_token.token == token
        assert refresh_token.expires_at == expires_at
        assert refresh_token.is_revoked is True
        assert refresh_token.created_at == created_at

    def test_refresh_token_tablename(self) -> None:
        """Test that the table name is correctly set."""
        assert RefreshToken.__tablename__ == "refresh_tokens"

    def test_refresh_token_repr(self) -> None:
        """Test the string representation of a RefreshToken."""
        token_id = str(uuid4())
        user_id = str(uuid4())
        expires_at = datetime.now(UTC) + timedelta(days=7)

        refresh_token = RefreshToken(
            id=token_id,
            user_id=user_id,
            token="repr_test_token",
            expires_at=expires_at,
            is_revoked=False,
        )

        repr_str = repr(refresh_token)
        assert token_id in repr_str
        assert user_id in repr_str
        assert "is_revoked=False" in repr_str


class TestRefreshTokenProperties:
    """Tests for RefreshToken property methods."""

    def test_is_expired_with_future_date(self) -> None:
        """Test is_expired returns False for future expiration."""
        refresh_token = RefreshToken(
            user_id=str(uuid4()),
            token="future_token",
            expires_at=datetime.now(UTC) + timedelta(days=7),
        )

        assert refresh_token.is_expired is False

    def test_is_expired_with_past_date(self) -> None:
        """Test is_expired returns True for past expiration."""
        refresh_token = RefreshToken(
            user_id=str(uuid4()),
            token="expired_token",
            expires_at=datetime.now(UTC) - timedelta(days=1),
        )

        assert refresh_token.is_expired is True

    def test_is_valid_with_valid_token(self) -> None:
        """Test is_valid returns True for valid, non-revoked token."""
        refresh_token = RefreshToken(
            user_id=str(uuid4()),
            token="valid_token",
            expires_at=datetime.now(UTC) + timedelta(days=7),
            is_revoked=False,
        )

        assert refresh_token.is_valid is True

    def test_is_valid_with_revoked_token(self) -> None:
        """Test is_valid returns False for revoked token."""
        refresh_token = RefreshToken(
            user_id=str(uuid4()),
            token="revoked_token",
            expires_at=datetime.now(UTC) + timedelta(days=7),
            is_revoked=True,
        )

        assert refresh_token.is_valid is False

    def test_is_valid_with_expired_token(self) -> None:
        """Test is_valid returns False for expired token."""
        refresh_token = RefreshToken(
            user_id=str(uuid4()),
            token="expired_token",
            expires_at=datetime.now(UTC) - timedelta(days=1),
            is_revoked=False,
        )

        assert refresh_token.is_valid is False

    def test_is_valid_with_expired_and_revoked_token(self) -> None:
        """Test is_valid returns False for expired and revoked token."""
        refresh_token = RefreshToken(
            user_id=str(uuid4()),
            token="expired_revoked_token",
            expires_at=datetime.now(UTC) - timedelta(days=1),
            is_revoked=True,
        )

        assert refresh_token.is_valid is False


class TestRefreshTokenMethods:
    """Tests for RefreshToken methods."""

    def test_revoke_sets_is_revoked_to_true(self) -> None:
        """Test that revoke() sets is_revoked to True."""
        refresh_token = RefreshToken(
            user_id=str(uuid4()),
            token="to_revoke_token",
            expires_at=datetime.now(UTC) + timedelta(days=7),
            is_revoked=False,
        )

        assert refresh_token.is_revoked is False
        refresh_token.revoke()
        assert refresh_token.is_revoked is True

    def test_revoke_on_already_revoked_token(self) -> None:
        """Test that revoke() on already revoked token keeps it revoked."""
        refresh_token = RefreshToken(
            user_id=str(uuid4()),
            token="already_revoked_token",
            expires_at=datetime.now(UTC) + timedelta(days=7),
            is_revoked=True,
        )

        refresh_token.revoke()
        assert refresh_token.is_revoked is True

    def test_cleanup_expired_query(self) -> None:
        """Test cleanup_expired_query returns correct query hint."""
        query_hint = RefreshToken.cleanup_expired_query()

        assert "DELETE FROM refresh_tokens" in query_hint
        assert "expires_at < NOW()" in query_hint
        assert "is_revoked = TRUE" in query_hint


class TestRefreshTokenDatabase:
    """Tests for RefreshToken database operations."""

    @pytest.mark.asyncio
    async def test_save_refresh_token(self, async_session: AsyncSession) -> None:
        """Test saving a RefreshToken to the database."""
        # Create organization first
        org = Organization(
            name="Test Org for Token",
            slug="test-org-token",
        )
        async_session.add(org)
        await async_session.flush()

        # Create user
        user = User(
            organization_id=org.id,
            email="tokenuser@example.com",
            first_name="Token",
            last_name="User",
        )
        user.set_password("securepassword123")
        async_session.add(user)
        await async_session.flush()

        # Create refresh token
        refresh_token = RefreshToken(
            user_id=user.id,
            token="db_test_token_abc123",
            expires_at=datetime.now(UTC) + timedelta(days=7),
        )
        async_session.add(refresh_token)
        await async_session.commit()

        # Verify token was saved
        result = await async_session.execute(
            select(RefreshToken).where(RefreshToken.id == refresh_token.id)
        )
        saved_token = result.scalar_one()

        assert saved_token.id == refresh_token.id
        assert saved_token.user_id == user.id
        assert saved_token.token == "db_test_token_abc123"
        assert saved_token.is_revoked is False
        assert saved_token.created_at is not None

    @pytest.mark.asyncio
    async def test_token_uniqueness(self, async_session: AsyncSession) -> None:
        """Test that token values must be unique."""
        # Create organization and user
        org = Organization(
            name="Unique Test Org",
            slug="unique-test-org",
        )
        async_session.add(org)
        await async_session.flush()

        user = User(
            organization_id=org.id,
            email="uniqueuser@example.com",
            first_name="Unique",
            last_name="User",
        )
        user.set_password("password123")
        async_session.add(user)
        await async_session.flush()

        # Create first token
        token1 = RefreshToken(
            user_id=user.id,
            token="unique_token_value",
            expires_at=datetime.now(UTC) + timedelta(days=7),
        )
        async_session.add(token1)
        await async_session.commit()

        # Try to create second token with same value
        token2 = RefreshToken(
            user_id=user.id,
            token="unique_token_value",  # Same token value
            expires_at=datetime.now(UTC) + timedelta(days=14),
        )
        async_session.add(token2)

        with pytest.raises((Exception,), match="UNIQUE constraint"):
            await async_session.commit()

    @pytest.mark.asyncio
    async def test_cascade_delete_on_user_deletion(
        self, async_session: AsyncSession
    ) -> None:
        """Test that tokens are deleted when user is deleted."""
        # Create organization
        org = Organization(
            name="Cascade Test Org",
            slug="cascade-test-org",
        )
        async_session.add(org)
        await async_session.flush()

        # Create user
        user = User(
            organization_id=org.id,
            email="cascadeuser@example.com",
            first_name="Cascade",
            last_name="User",
        )
        user.set_password("password123")
        async_session.add(user)
        await async_session.flush()

        user_id = user.id

        # Create multiple tokens
        for i in range(3):
            token = RefreshToken(
                user_id=user.id,
                token=f"cascade_token_{i}",
                expires_at=datetime.now(UTC) + timedelta(days=7),
            )
            async_session.add(token)
        await async_session.commit()

        # Verify tokens exist
        result = await async_session.execute(
            select(RefreshToken).where(RefreshToken.user_id == user_id)
        )
        tokens = result.scalars().all()
        assert len(tokens) == 3

        # Delete user
        await async_session.delete(user)
        await async_session.commit()

        # Verify tokens are deleted
        result = await async_session.execute(
            select(RefreshToken).where(RefreshToken.user_id == user_id)
        )
        tokens = result.scalars().all()
        assert len(tokens) == 0


class TestRefreshTokenUserRelationship:
    """Tests for RefreshToken-User relationship."""

    @pytest.mark.asyncio
    async def test_access_user_from_token(self, async_session: AsyncSession) -> None:
        """Test accessing user from refresh token relationship."""
        # Create organization
        org = Organization(
            name="Relation Test Org",
            slug="relation-test-org",
        )
        async_session.add(org)
        await async_session.flush()

        # Create user
        user = User(
            organization_id=org.id,
            email="relationuser@example.com",
            first_name="Relation",
            last_name="User",
        )
        user.set_password("password123")
        async_session.add(user)
        await async_session.flush()

        # Create token
        token = RefreshToken(
            user_id=user.id,
            token="relation_test_token",
            expires_at=datetime.now(UTC) + timedelta(days=7),
        )
        async_session.add(token)
        await async_session.commit()

        # Refresh to get relationships
        await async_session.refresh(token)

        assert token.user is not None
        assert token.user.id == user.id
        assert token.user.email == "relationuser@example.com"

    @pytest.mark.asyncio
    async def test_access_tokens_from_user(self, async_session: AsyncSession) -> None:
        """Test accessing refresh tokens from user relationship."""
        # Create organization
        org = Organization(
            name="Tokens List Org",
            slug="tokens-list-org",
        )
        async_session.add(org)
        await async_session.flush()

        # Create user
        user = User(
            organization_id=org.id,
            email="tokenslistuser@example.com",
            first_name="TokensList",
            last_name="User",
        )
        user.set_password("password123")
        async_session.add(user)
        await async_session.flush()

        # Create multiple tokens
        for i in range(2):
            token = RefreshToken(
                user_id=user.id,
                token=f"list_token_{i}",
                expires_at=datetime.now(UTC) + timedelta(days=7),
            )
            async_session.add(token)
        await async_session.commit()

        # Refresh to get relationships
        await async_session.refresh(user)

        assert len(user.refresh_tokens) == 2
        assert all(t.user_id == user.id for t in user.refresh_tokens)

    @pytest.mark.asyncio
    async def test_multiple_tokens_per_user(self, async_session: AsyncSession) -> None:
        """Test that a user can have multiple refresh tokens."""
        # Create organization
        org = Organization(
            name="Multi Token Org",
            slug="multi-token-org",
        )
        async_session.add(org)
        await async_session.flush()

        # Create user
        user = User(
            organization_id=org.id,
            email="multitokenuser@example.com",
            first_name="MultiToken",
            last_name="User",
        )
        user.set_password("password123")
        async_session.add(user)
        await async_session.flush()

        # Create tokens with different expiration dates
        tokens_data = [
            ("token_device_1", timedelta(days=7)),
            ("token_device_2", timedelta(days=14)),
            ("token_device_3", timedelta(days=30)),
        ]

        for token_value, delta in tokens_data:
            token = RefreshToken(
                user_id=user.id,
                token=token_value,
                expires_at=datetime.now(UTC) + delta,
            )
            async_session.add(token)
        await async_session.commit()

        # Verify all tokens exist
        result = await async_session.execute(
            select(RefreshToken).where(RefreshToken.user_id == user.id)
        )
        tokens = result.scalars().all()

        assert len(tokens) == 3
        token_values = [t.token for t in tokens]
        assert "token_device_1" in token_values
        assert "token_device_2" in token_values
        assert "token_device_3" in token_values
