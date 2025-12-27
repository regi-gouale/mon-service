"""
Unit tests for API v1 dependencies.

Tests authentication dependencies including:
- get_current_user
- get_current_active_user
- get_current_verified_user
- get_optional_current_user
- require_role
"""

from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import jwt
import pytest
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials

from app.api.v1.dependencies import (
    get_current_active_user,
    get_current_user,
    get_current_verified_user,
    get_optional_current_user,
    require_role,
)
from app.core.config import get_settings
from app.models.user import User, UserRole

settings = get_settings()


# ============================================================================
# Fixtures
# ============================================================================


@pytest.fixture
def mock_session() -> AsyncMock:
    """Create a mock database session."""
    return AsyncMock()


@pytest.fixture
def sample_user_id() -> str:
    """Generate a sample user ID."""
    return str(uuid4())


@pytest.fixture
def active_user(sample_user_id: str) -> User:
    """Create an active user for testing."""
    user = MagicMock(spec=User)
    user.id = sample_user_id
    user.email = "test@example.com"
    user.is_active = True
    user.email_verified = True
    user.role = UserRole.MEMBER
    return user


@pytest.fixture
def inactive_user(sample_user_id: str) -> User:
    """Create an inactive user for testing."""
    user = MagicMock(spec=User)
    user.id = sample_user_id
    user.email = "inactive@example.com"
    user.is_active = False
    user.email_verified = True
    user.role = UserRole.MEMBER
    return user


@pytest.fixture
def unverified_user(sample_user_id: str) -> User:
    """Create a user with unverified email for testing."""
    user = MagicMock(spec=User)
    user.id = sample_user_id
    user.email = "unverified@example.com"
    user.is_active = True
    user.email_verified = False
    user.role = UserRole.MEMBER
    return user


@pytest.fixture
def admin_user(sample_user_id: str) -> User:
    """Create an admin user for testing."""
    user = MagicMock(spec=User)
    user.id = sample_user_id
    user.email = "admin@example.com"
    user.is_active = True
    user.email_verified = True
    user.role = UserRole.ADMIN
    return user


def create_access_token(
    user_id: str,
    token_type: str = "access",
    expires_delta: timedelta | None = None,
) -> str:
    """Create a JWT access token for testing."""
    if expires_delta is None:
        expires_delta = timedelta(minutes=30)

    expire = datetime.now(UTC) + expires_delta
    payload = {
        "sub": user_id,
        "type": token_type,
        "exp": expire,
        "iat": datetime.now(UTC),
    }
    return jwt.encode(
        payload,
        settings.secret_key,
        algorithm=settings.jwt_algorithm,
    )


def create_credentials(token: str) -> HTTPAuthorizationCredentials:
    """Create HTTP Bearer credentials from a token."""
    return HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)


# ============================================================================
# Tests for get_current_user
# ============================================================================


class TestGetCurrentUser:
    """Tests for the get_current_user dependency."""

    @pytest.mark.asyncio
    async def test_returns_user_with_valid_token(
        self,
        mock_session: AsyncMock,
        active_user: User,
        sample_user_id: str,
    ) -> None:
        """Test that get_current_user returns user with valid token."""
        token = create_access_token(sample_user_id)
        credentials = create_credentials(token)

        with patch("app.api.v1.dependencies.UserRepository") as mock_repo_class:
            mock_repo = AsyncMock()
            mock_repo.get_by_id.return_value = active_user
            mock_repo_class.return_value = mock_repo

            result = await get_current_user(credentials, mock_session)

            assert result == active_user
            mock_repo.get_by_id.assert_called_once_with(sample_user_id)

    @pytest.mark.asyncio
    async def test_raises_401_when_no_credentials(
        self,
        mock_session: AsyncMock,
    ) -> None:
        """Test that get_current_user raises 401 when no credentials."""
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(None, mock_session)

        assert exc_info.value.status_code == 401
        assert exc_info.value.detail == "Authentication required"
        assert exc_info.value.headers == {"WWW-Authenticate": "Bearer"}

    @pytest.mark.asyncio
    async def test_raises_401_when_token_expired(
        self,
        mock_session: AsyncMock,
        sample_user_id: str,
    ) -> None:
        """Test that get_current_user raises 401 when token expired."""
        expired_token = create_access_token(
            sample_user_id,
            expires_delta=timedelta(minutes=-5),
        )
        credentials = create_credentials(expired_token)

        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(credentials, mock_session)

        assert exc_info.value.status_code == 401
        assert exc_info.value.detail == "Token has expired"

    @pytest.mark.asyncio
    async def test_raises_401_when_token_invalid(
        self,
        mock_session: AsyncMock,
    ) -> None:
        """Test that get_current_user raises 401 when token is invalid."""
        credentials = create_credentials("invalid.token.here")

        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(credentials, mock_session)

        assert exc_info.value.status_code == 401
        assert exc_info.value.detail == "Invalid authentication token"

    @pytest.mark.asyncio
    async def test_raises_401_when_wrong_token_type(
        self,
        mock_session: AsyncMock,
        sample_user_id: str,
    ) -> None:
        """Test that get_current_user raises 401 with refresh token."""
        refresh_token = create_access_token(
            sample_user_id,
            token_type="refresh",
        )
        credentials = create_credentials(refresh_token)

        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(credentials, mock_session)

        assert exc_info.value.status_code == 401
        assert exc_info.value.detail == "Invalid token type"

    @pytest.mark.asyncio
    async def test_raises_401_when_no_subject_in_token(
        self,
        mock_session: AsyncMock,
    ) -> None:
        """Test that get_current_user raises 401 when no sub in token."""
        # Create token without subject
        expire = datetime.now(UTC) + timedelta(minutes=30)
        payload = {
            "type": "access",
            "exp": expire,
            "iat": datetime.now(UTC),
        }
        token = jwt.encode(
            payload,
            settings.secret_key,
            algorithm=settings.jwt_algorithm,
        )
        credentials = create_credentials(token)

        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(credentials, mock_session)

        assert exc_info.value.status_code == 401
        assert exc_info.value.detail == "Invalid token payload"

    @pytest.mark.asyncio
    async def test_raises_401_when_user_not_found(
        self,
        mock_session: AsyncMock,
        sample_user_id: str,
    ) -> None:
        """Test that get_current_user raises 401 when user not in DB."""
        token = create_access_token(sample_user_id)
        credentials = create_credentials(token)

        with patch("app.api.v1.dependencies.UserRepository") as mock_repo_class:
            mock_repo = AsyncMock()
            mock_repo.get_by_id.return_value = None
            mock_repo_class.return_value = mock_repo

            with pytest.raises(HTTPException) as exc_info:
                await get_current_user(credentials, mock_session)

            assert exc_info.value.status_code == 401
            assert exc_info.value.detail == "User not found"


# ============================================================================
# Tests for get_current_active_user
# ============================================================================


class TestGetCurrentActiveUser:
    """Tests for the get_current_active_user dependency."""

    @pytest.mark.asyncio
    async def test_returns_active_user(self, active_user: User) -> None:
        """Test that get_current_active_user returns active user."""
        result = await get_current_active_user(active_user)
        assert result == active_user

    @pytest.mark.asyncio
    async def test_raises_403_for_inactive_user(
        self,
        inactive_user: User,
    ) -> None:
        """Test that get_current_active_user raises 403 for inactive."""
        with pytest.raises(HTTPException) as exc_info:
            await get_current_active_user(inactive_user)

        assert exc_info.value.status_code == 403
        assert exc_info.value.detail == "User account is deactivated"


# ============================================================================
# Tests for get_current_verified_user
# ============================================================================


class TestGetCurrentVerifiedUser:
    """Tests for the get_current_verified_user dependency."""

    @pytest.mark.asyncio
    async def test_returns_verified_user(self, active_user: User) -> None:
        """Test that get_current_verified_user returns verified user."""
        result = await get_current_verified_user(active_user)
        assert result == active_user

    @pytest.mark.asyncio
    async def test_raises_403_for_unverified_user(
        self,
        unverified_user: User,
    ) -> None:
        """Test that get_current_verified_user raises 403 for unverified."""
        with pytest.raises(HTTPException) as exc_info:
            await get_current_verified_user(unverified_user)

        assert exc_info.value.status_code == 403
        assert exc_info.value.detail == "Email verification required"


# ============================================================================
# Tests for require_role
# ============================================================================


class TestRequireRole:
    """Tests for the require_role dependency factory."""

    @pytest.mark.asyncio
    async def test_allows_user_with_correct_role(
        self,
        admin_user: User,
    ) -> None:
        """Test that require_role allows user with correct role."""
        role_checker = require_role(UserRole.ADMIN)
        result = await role_checker(admin_user)
        assert result == admin_user

    @pytest.mark.asyncio
    async def test_allows_user_with_one_of_multiple_roles(
        self,
        admin_user: User,
    ) -> None:
        """Test that require_role allows user with one of multiple roles."""
        role_checker = require_role(UserRole.ADMIN, UserRole.MANAGER)
        result = await role_checker(admin_user)
        assert result == admin_user

    @pytest.mark.asyncio
    async def test_raises_403_for_insufficient_role(
        self,
        active_user: User,  # Has MEMBER role
    ) -> None:
        """Test that require_role raises 403 for insufficient role."""
        role_checker = require_role(UserRole.ADMIN)

        with pytest.raises(HTTPException) as exc_info:
            await role_checker(active_user)

        assert exc_info.value.status_code == 403
        assert exc_info.value.detail == "Insufficient permissions"

    @pytest.mark.asyncio
    async def test_handles_string_role(self, sample_user_id: str) -> None:
        """Test that require_role handles string role values."""
        user = MagicMock(spec=User)
        user.id = sample_user_id
        user.is_active = True
        user.role = "admin"  # String instead of enum

        role_checker = require_role(UserRole.ADMIN)
        result = await role_checker(user)
        assert result == user


# ============================================================================
# Tests for get_optional_current_user
# ============================================================================


class TestGetOptionalCurrentUser:
    """Tests for the get_optional_current_user dependency."""

    @pytest.mark.asyncio
    async def test_returns_user_with_valid_token(
        self,
        mock_session: AsyncMock,
        active_user: User,
        sample_user_id: str,
    ) -> None:
        """Test that get_optional_current_user returns user with valid token."""
        token = create_access_token(sample_user_id)
        credentials = create_credentials(token)

        with patch("app.api.v1.dependencies.UserRepository") as mock_repo_class:
            mock_repo = AsyncMock()
            mock_repo.get_by_id.return_value = active_user
            mock_repo_class.return_value = mock_repo

            result = await get_optional_current_user(credentials, mock_session)

            assert result == active_user

    @pytest.mark.asyncio
    async def test_returns_none_when_no_credentials(
        self,
        mock_session: AsyncMock,
    ) -> None:
        """Test that get_optional_current_user returns None without creds."""
        result = await get_optional_current_user(None, mock_session)
        assert result is None

    @pytest.mark.asyncio
    async def test_returns_none_when_token_expired(
        self,
        mock_session: AsyncMock,
        sample_user_id: str,
    ) -> None:
        """Test that get_optional_current_user returns None for expired token."""
        expired_token = create_access_token(
            sample_user_id,
            expires_delta=timedelta(minutes=-5),
        )
        credentials = create_credentials(expired_token)

        result = await get_optional_current_user(credentials, mock_session)
        assert result is None

    @pytest.mark.asyncio
    async def test_returns_none_when_token_invalid(
        self,
        mock_session: AsyncMock,
    ) -> None:
        """Test that get_optional_current_user returns None for invalid token."""
        credentials = create_credentials("invalid.token")

        result = await get_optional_current_user(credentials, mock_session)
        assert result is None

    @pytest.mark.asyncio
    async def test_returns_none_when_wrong_token_type(
        self,
        mock_session: AsyncMock,
        sample_user_id: str,
    ) -> None:
        """Test that get_optional_current_user returns None for refresh token."""
        refresh_token = create_access_token(
            sample_user_id,
            token_type="refresh",
        )
        credentials = create_credentials(refresh_token)

        result = await get_optional_current_user(credentials, mock_session)
        assert result is None

    @pytest.mark.asyncio
    async def test_returns_none_when_no_subject_in_token(
        self,
        mock_session: AsyncMock,
    ) -> None:
        """Test that get_optional_current_user returns None without sub."""
        expire = datetime.now(UTC) + timedelta(minutes=30)
        payload = {
            "type": "access",
            "exp": expire,
        }
        token = jwt.encode(
            payload,
            settings.secret_key,
            algorithm=settings.jwt_algorithm,
        )
        credentials = create_credentials(token)

        result = await get_optional_current_user(credentials, mock_session)
        assert result is None

    @pytest.mark.asyncio
    async def test_returns_none_when_user_not_found(
        self,
        mock_session: AsyncMock,
        sample_user_id: str,
    ) -> None:
        """Test that get_optional_current_user returns None if user missing."""
        token = create_access_token(sample_user_id)
        credentials = create_credentials(token)

        with patch("app.api.v1.dependencies.UserRepository") as mock_repo_class:
            mock_repo = AsyncMock()
            mock_repo.get_by_id.return_value = None
            mock_repo_class.return_value = mock_repo

            result = await get_optional_current_user(credentials, mock_session)
            assert result is None

    @pytest.mark.asyncio
    async def test_returns_none_when_user_inactive(
        self,
        mock_session: AsyncMock,
        inactive_user: User,
        sample_user_id: str,
    ) -> None:
        """Test that get_optional_current_user returns None if user inactive."""
        token = create_access_token(sample_user_id)
        credentials = create_credentials(token)

        with patch("app.api.v1.dependencies.UserRepository") as mock_repo_class:
            mock_repo = AsyncMock()
            mock_repo.get_by_id.return_value = inactive_user
            mock_repo_class.return_value = mock_repo

            result = await get_optional_current_user(credentials, mock_session)
            assert result is None
