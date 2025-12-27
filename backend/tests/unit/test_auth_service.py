"""
Unit Tests for AuthService.

Tests for authentication service business logic including
registration, login, token management, and password reset.
"""

from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

import jwt
import pytest

from app.core.config import settings
from app.core.exceptions import (
    AlreadyExistsError,
    NotFoundError,
    UnauthorizedError,
)
from app.models.refresh_token import RefreshToken
from app.models.user import User, UserRole
from app.schemas.auth import RegisterRequest
from app.services.auth_service import AuthService


@pytest.fixture
def mock_session() -> AsyncMock:
    """Create a mock async session."""
    session = AsyncMock()
    session.commit = AsyncMock()
    session.flush = AsyncMock()
    session.rollback = AsyncMock()
    session.add = MagicMock()
    session.execute = AsyncMock()
    return session


@pytest.fixture
def auth_service(mock_session: AsyncMock) -> AuthService:
    """Create an AuthService instance with mock session."""
    return AuthService(mock_session)


@pytest.fixture
def sample_user() -> User:
    """Create a sample user for testing."""
    user = User(
        id="user-123",
        email="test@example.com",
        password_hash="$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4.G8b5MxXgIHHHHH",
        first_name="Test",
        last_name="User",
        role=UserRole.MEMBER,
        email_verified=False,
        is_active=True,
        created_at=datetime.now(UTC),
    )
    return user


@pytest.fixture
def sample_refresh_token(sample_user: User) -> RefreshToken:
    """Create a sample refresh token for testing."""
    return RefreshToken(
        id="token-123",
        user_id=sample_user.id,
        token="valid-refresh-token",
        expires_at=datetime.now(UTC) + timedelta(days=7),
        is_revoked=False,
        created_at=datetime.now(UTC),
    )


class TestRegister:
    """Tests for AuthService.register method."""

    @pytest.mark.asyncio
    async def test_register_success(
        self,
        auth_service: AuthService,
        mock_session: AsyncMock,
    ) -> None:
        """Test successful user registration."""
        # Arrange
        register_data = RegisterRequest(
            email="new@example.com",
            password="SecureP@ss123",
            first_name="New",
            last_name="User",
        )

        created_user = User(
            id="new-user-123",
            email="new@example.com",
            password_hash="hashed",
            first_name="New",
            last_name="User",
            role=UserRole.MEMBER,
            email_verified=False,
            is_active=True,
            created_at=datetime.now(UTC),
        )

        # Mock repository methods
        auth_service.user_repository.get_by_email = AsyncMock(return_value=None)
        auth_service.user_repository.create = AsyncMock(return_value=created_user)

        # Act
        result = await auth_service.register(register_data)

        # Assert
        assert result.user.email == "new@example.com"
        assert result.user.first_name == "New"
        assert result.user.last_name == "User"
        assert result.access_token is not None
        assert result.refresh_token is not None
        assert result.token_type == "bearer"
        mock_session.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_register_email_already_exists(
        self,
        auth_service: AuthService,
        sample_user: User,
    ) -> None:
        """Test registration fails when email already exists."""
        # Arrange
        register_data = RegisterRequest(
            email="test@example.com",
            password="SecureP@ss123",
            first_name="Test",
            last_name="User",
        )

        auth_service.user_repository.get_by_email = AsyncMock(return_value=sample_user)

        # Act & Assert
        with pytest.raises(AlreadyExistsError) as exc_info:
            await auth_service.register(register_data)

        assert "email" in str(exc_info.value.message).lower()

    @pytest.mark.asyncio
    async def test_register_with_organization(
        self,
        auth_service: AuthService,
        mock_session: AsyncMock,  # noqa: ARG002
    ) -> None:
        """Test registration with organization ID."""
        # Arrange
        register_data = RegisterRequest(
            email="org@example.com",
            password="SecureP@ss123",
            first_name="Org",
            last_name="User",
        )
        org_id = "org-123"

        created_user = User(
            id="org-user-123",
            email="org@example.com",
            password_hash="hashed",
            first_name="Org",
            last_name="User",
            organization_id=org_id,
            role=UserRole.MEMBER,
            email_verified=False,
            is_active=True,
            created_at=datetime.now(UTC),
        )

        auth_service.user_repository.get_by_email = AsyncMock(return_value=None)
        auth_service.user_repository.create = AsyncMock(return_value=created_user)

        # Act
        result = await auth_service.register(register_data, organization_id=org_id)

        # Assert
        assert result.user.email == "org@example.com"
        auth_service.user_repository.create.assert_called_once()


class TestLogin:
    """Tests for AuthService.login method."""

    @pytest.mark.asyncio
    async def test_login_success(
        self,
        auth_service: AuthService,
        sample_user: User,
        mock_session: AsyncMock,  # noqa: ARG002
    ) -> None:
        """Test successful login."""
        # Arrange
        auth_service.user_repository.get_by_email = AsyncMock(return_value=sample_user)
        auth_service.user_repository.update_last_login = AsyncMock()

        with patch("app.services.auth_service.verify_password", return_value=True):
            # Act
            result = await auth_service.login("test@example.com", "ValidPassword123!")

        # Assert
        assert result.user.email == "test@example.com"
        assert result.access_token is not None
        assert result.refresh_token is not None
        auth_service.user_repository.update_last_login.assert_called_once_with(
            sample_user.id
        )

    @pytest.mark.asyncio
    async def test_login_user_not_found(
        self,
        auth_service: AuthService,
    ) -> None:
        """Test login fails when user not found."""
        # Arrange
        auth_service.user_repository.get_by_email = AsyncMock(return_value=None)

        # Act & Assert
        with pytest.raises(UnauthorizedError) as exc_info:
            await auth_service.login("unknown@example.com", "password")

        assert "invalid" in str(exc_info.value.message).lower()

    @pytest.mark.asyncio
    async def test_login_invalid_password(
        self,
        auth_service: AuthService,
        sample_user: User,
    ) -> None:
        """Test login fails with wrong password."""
        # Arrange
        auth_service.user_repository.get_by_email = AsyncMock(return_value=sample_user)

        # Act & Assert
        with (
            patch("app.services.auth_service.verify_password", return_value=False),
            pytest.raises(UnauthorizedError) as exc_info,
        ):
            await auth_service.login("test@example.com", "WrongPassword!")

        assert "invalid" in str(exc_info.value.message).lower()

    @pytest.mark.asyncio
    async def test_login_inactive_account(
        self,
        auth_service: AuthService,
        sample_user: User,
    ) -> None:
        """Test login fails when account is inactive."""
        # Arrange
        sample_user.is_active = False
        auth_service.user_repository.get_by_email = AsyncMock(return_value=sample_user)

        # Act & Assert
        with pytest.raises(UnauthorizedError) as exc_info:
            await auth_service.login("test@example.com", "password")

        assert "deactivated" in str(exc_info.value.message).lower()

    @pytest.mark.asyncio
    async def test_login_oauth_user_no_password(
        self,
        auth_service: AuthService,
        sample_user: User,
    ) -> None:
        """Test login fails for OAuth user without password."""
        # Arrange
        sample_user.password_hash = None
        auth_service.user_repository.get_by_email = AsyncMock(return_value=sample_user)

        # Act & Assert
        with pytest.raises(UnauthorizedError):
            await auth_service.login("test@example.com", "password")


class TestRefreshToken:
    """Tests for AuthService.refresh_token method."""

    @pytest.mark.asyncio
    async def test_refresh_token_success(
        self,
        auth_service: AuthService,
        sample_user: User,
        sample_refresh_token: RefreshToken,
        mock_session: AsyncMock,
    ) -> None:
        """Test successful token refresh."""
        # Arrange
        valid_token = jwt.encode(
            {
                "sub": sample_user.id,
                "type": "refresh",
                "exp": datetime.now(UTC) + timedelta(days=7),
                "iat": datetime.now(UTC),
            },
            settings.secret_key,
            algorithm=settings.jwt_algorithm,
        )

        sample_refresh_token.token = valid_token

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_refresh_token
        mock_session.execute.return_value = mock_result

        auth_service.user_repository.get_by_id = AsyncMock(return_value=sample_user)

        # Act
        result = await auth_service.refresh_token(valid_token)

        # Assert
        assert result.access_token is not None
        assert result.refresh_token is not None
        assert result.user.id == sample_user.id
        assert sample_refresh_token.is_revoked is True  # Old token revoked

    @pytest.mark.asyncio
    async def test_refresh_token_expired(
        self,
        auth_service: AuthService,
        sample_user: User,
    ) -> None:
        """Test refresh fails with expired token."""
        # Arrange
        expired_token = jwt.encode(
            {
                "sub": sample_user.id,
                "type": "refresh",
                "exp": datetime.now(UTC) - timedelta(hours=1),
                "iat": datetime.now(UTC) - timedelta(days=1),
            },
            settings.secret_key,
            algorithm=settings.jwt_algorithm,
        )

        # Act & Assert
        with pytest.raises(UnauthorizedError) as exc_info:
            await auth_service.refresh_token(expired_token)

        assert "expired" in str(exc_info.value.message).lower()

    @pytest.mark.asyncio
    async def test_refresh_token_invalid(
        self,
        auth_service: AuthService,
    ) -> None:
        """Test refresh fails with invalid token."""
        # Act & Assert
        with pytest.raises(UnauthorizedError) as exc_info:
            await auth_service.refresh_token("invalid-token")

        assert "invalid" in str(exc_info.value.message).lower()

    @pytest.mark.asyncio
    async def test_refresh_token_wrong_type(
        self,
        auth_service: AuthService,
        sample_user: User,
    ) -> None:
        """Test refresh fails with access token instead of refresh token."""
        # Arrange
        access_token = jwt.encode(
            {
                "sub": sample_user.id,
                "type": "access",  # Wrong type
                "exp": datetime.now(UTC) + timedelta(minutes=15),
            },
            settings.secret_key,
            algorithm=settings.jwt_algorithm,
        )

        # Act & Assert
        with pytest.raises(UnauthorizedError) as exc_info:
            await auth_service.refresh_token(access_token)

        assert "type" in str(exc_info.value.message).lower()

    @pytest.mark.asyncio
    async def test_refresh_token_revoked(
        self,
        auth_service: AuthService,
        sample_user: User,
        mock_session: AsyncMock,
    ) -> None:
        """Test refresh fails when token is revoked."""
        # Arrange
        valid_token = jwt.encode(
            {
                "sub": sample_user.id,
                "type": "refresh",
                "exp": datetime.now(UTC) + timedelta(days=7),
            },
            settings.secret_key,
            algorithm=settings.jwt_algorithm,
        )

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None  # Token not found
        mock_session.execute.return_value = mock_result

        # Act & Assert
        with pytest.raises(UnauthorizedError) as exc_info:
            await auth_service.refresh_token(valid_token)

        assert "revoked" in str(exc_info.value.message).lower()

    @pytest.mark.asyncio
    async def test_refresh_token_user_inactive(
        self,
        auth_service: AuthService,
        sample_user: User,
        sample_refresh_token: RefreshToken,
        mock_session: AsyncMock,
    ) -> None:
        """Test refresh fails when user is inactive."""
        # Arrange
        valid_token = jwt.encode(
            {
                "sub": sample_user.id,
                "type": "refresh",
                "exp": datetime.now(UTC) + timedelta(days=7),
            },
            settings.secret_key,
            algorithm=settings.jwt_algorithm,
        )

        sample_refresh_token.token = valid_token

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_refresh_token
        mock_session.execute.return_value = mock_result

        sample_user.is_active = False
        auth_service.user_repository.get_by_id = AsyncMock(return_value=sample_user)

        # Act & Assert
        with pytest.raises(UnauthorizedError) as exc_info:
            await auth_service.refresh_token(valid_token)

        assert "inactive" in str(exc_info.value.message).lower()


class TestLogout:
    """Tests for AuthService.logout method."""

    @pytest.mark.asyncio
    async def test_logout_specific_token(
        self,
        auth_service: AuthService,
        sample_refresh_token: RefreshToken,
        mock_session: AsyncMock,
    ) -> None:
        """Test logout with specific token."""
        # Arrange
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_refresh_token
        mock_session.execute.return_value = mock_result

        # Act
        await auth_service.logout("user-123", "valid-refresh-token")

        # Assert
        assert sample_refresh_token.is_revoked is True
        mock_session.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_logout_revoke_all(
        self,
        auth_service: AuthService,
        mock_session: AsyncMock,
    ) -> None:
        """Test logout with revoke_all flag."""
        # Act
        await auth_service.logout("user-123", revoke_all=True)

        # Assert
        mock_session.execute.assert_called_once()
        mock_session.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_logout_token_not_found(
        self,
        auth_service: AuthService,
        mock_session: AsyncMock,
    ) -> None:
        """Test logout fails when token not found."""
        # Arrange
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result

        # Act & Assert
        with pytest.raises(NotFoundError):
            await auth_service.logout("user-123", "nonexistent-token")

    @pytest.mark.asyncio
    async def test_logout_without_token(
        self,
        auth_service: AuthService,
        mock_session: AsyncMock,
    ) -> None:
        """Test logout without specifying token or revoke_all."""
        # Act
        await auth_service.logout("user-123")

        # Assert - should succeed without revoking anything
        mock_session.commit.assert_called_once()


class TestForgotPassword:
    """Tests for AuthService.forgot_password method."""

    @pytest.mark.asyncio
    async def test_forgot_password_success(
        self,
        auth_service: AuthService,
        sample_user: User,
    ) -> None:
        """Test forgot password generates reset token."""
        # Arrange
        auth_service.user_repository.get_by_email = AsyncMock(return_value=sample_user)

        # Act
        token = await auth_service.forgot_password("test@example.com")

        # Assert
        assert token is not None
        # Verify it's a valid JWT
        payload = jwt.decode(
            token, settings.secret_key, algorithms=[settings.jwt_algorithm]
        )
        assert payload["sub"] == sample_user.id
        assert payload["type"] == "password_reset"

    @pytest.mark.asyncio
    async def test_forgot_password_user_not_found(
        self,
        auth_service: AuthService,
    ) -> None:
        """Test forgot password fails for unknown email."""
        # Arrange
        auth_service.user_repository.get_by_email = AsyncMock(return_value=None)

        # Act & Assert
        with pytest.raises(NotFoundError):
            await auth_service.forgot_password("unknown@example.com")


class TestResetPassword:
    """Tests for AuthService.reset_password method."""

    @pytest.mark.asyncio
    async def test_reset_password_success(
        self,
        auth_service: AuthService,
        sample_user: User,
        mock_session: AsyncMock,
    ) -> None:
        """Test successful password reset."""
        # Arrange
        reset_token = jwt.encode(
            {
                "sub": sample_user.id,
                "email": sample_user.email,
                "type": "password_reset",
                "exp": datetime.now(UTC) + timedelta(hours=1),
            },
            settings.secret_key,
            algorithm=settings.jwt_algorithm,
        )

        auth_service.user_repository.get_by_id = AsyncMock(return_value=sample_user)
        auth_service.user_repository.update = AsyncMock()

        # Act
        await auth_service.reset_password(reset_token, "NewSecureP@ss456")

        # Assert
        auth_service.user_repository.update.assert_called_once()
        mock_session.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_reset_password_expired_token(
        self,
        auth_service: AuthService,
        sample_user: User,
    ) -> None:
        """Test reset password fails with expired token."""
        # Arrange
        expired_token = jwt.encode(
            {
                "sub": sample_user.id,
                "type": "password_reset",
                "exp": datetime.now(UTC) - timedelta(hours=1),
            },
            settings.secret_key,
            algorithm=settings.jwt_algorithm,
        )

        # Act & Assert
        with pytest.raises(UnauthorizedError) as exc_info:
            await auth_service.reset_password(expired_token, "NewSecureP@ss456")

        assert "expired" in str(exc_info.value.message).lower()

    @pytest.mark.asyncio
    async def test_reset_password_invalid_token(
        self,
        auth_service: AuthService,
    ) -> None:
        """Test reset password fails with invalid token."""
        # Act & Assert
        with pytest.raises(UnauthorizedError) as exc_info:
            await auth_service.reset_password("invalid-token", "NewSecureP@ss456")

        assert "invalid" in str(exc_info.value.message).lower()

    @pytest.mark.asyncio
    async def test_reset_password_wrong_token_type(
        self,
        auth_service: AuthService,
        sample_user: User,
    ) -> None:
        """Test reset password fails with wrong token type."""
        # Arrange
        wrong_type_token = jwt.encode(
            {
                "sub": sample_user.id,
                "type": "refresh",  # Wrong type
                "exp": datetime.now(UTC) + timedelta(hours=1),
            },
            settings.secret_key,
            algorithm=settings.jwt_algorithm,
        )

        # Act & Assert
        with pytest.raises(UnauthorizedError) as exc_info:
            await auth_service.reset_password(wrong_type_token, "NewSecureP@ss456")

        assert "type" in str(exc_info.value.message).lower()

    @pytest.mark.asyncio
    async def test_reset_password_user_not_found(
        self,
        auth_service: AuthService,
        sample_user: User,
    ) -> None:
        """Test reset password fails when user not found."""
        # Arrange
        reset_token = jwt.encode(
            {
                "sub": sample_user.id,
                "type": "password_reset",
                "exp": datetime.now(UTC) + timedelta(hours=1),
            },
            settings.secret_key,
            algorithm=settings.jwt_algorithm,
        )

        auth_service.user_repository.get_by_id = AsyncMock(return_value=None)

        # Act & Assert
        with pytest.raises(UnauthorizedError):
            await auth_service.reset_password(reset_token, "NewSecureP@ss456")


class TestVerifyEmail:
    """Tests for AuthService.verify_email method."""

    @pytest.mark.asyncio
    async def test_verify_email_success(
        self,
        auth_service: AuthService,
        sample_user: User,
        mock_session: AsyncMock,
    ) -> None:
        """Test successful email verification."""
        # Arrange
        verification_token = jwt.encode(
            {
                "sub": sample_user.id,
                "email": sample_user.email,
                "type": "email_verification",
                "exp": datetime.now(UTC) + timedelta(hours=24),
            },
            settings.secret_key,
            algorithm=settings.jwt_algorithm,
        )

        auth_service.user_repository.verify_email = AsyncMock()

        # Act
        await auth_service.verify_email(verification_token)

        # Assert
        auth_service.user_repository.verify_email.assert_called_once_with(
            sample_user.id
        )
        mock_session.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_verify_email_expired_token(
        self,
        auth_service: AuthService,
        sample_user: User,
    ) -> None:
        """Test verify email fails with expired token."""
        # Arrange
        expired_token = jwt.encode(
            {
                "sub": sample_user.id,
                "type": "email_verification",
                "exp": datetime.now(UTC) - timedelta(hours=1),
            },
            settings.secret_key,
            algorithm=settings.jwt_algorithm,
        )

        # Act & Assert
        with pytest.raises(UnauthorizedError) as exc_info:
            await auth_service.verify_email(expired_token)

        assert "expired" in str(exc_info.value.message).lower()

    @pytest.mark.asyncio
    async def test_verify_email_wrong_token_type(
        self,
        auth_service: AuthService,
        sample_user: User,
    ) -> None:
        """Test verify email fails with wrong token type."""
        # Arrange
        wrong_type_token = jwt.encode(
            {
                "sub": sample_user.id,
                "type": "access",  # Wrong type
                "exp": datetime.now(UTC) + timedelta(hours=24),
            },
            settings.secret_key,
            algorithm=settings.jwt_algorithm,
        )

        # Act & Assert
        with pytest.raises(UnauthorizedError) as exc_info:
            await auth_service.verify_email(wrong_type_token)

        assert "type" in str(exc_info.value.message).lower()


class TestCreateEmailVerificationToken:
    """Tests for AuthService.create_email_verification_token method."""

    @pytest.mark.asyncio
    async def test_create_email_verification_token_success(
        self,
        auth_service: AuthService,
        sample_user: User,
    ) -> None:
        """Test successful email verification token creation."""
        # Arrange
        auth_service.user_repository.get_by_id = AsyncMock(return_value=sample_user)

        # Act
        token = await auth_service.create_email_verification_token(sample_user.id)

        # Assert
        assert token is not None
        payload = jwt.decode(
            token, settings.secret_key, algorithms=[settings.jwt_algorithm]
        )
        assert payload["sub"] == sample_user.id
        assert payload["type"] == "email_verification"

    @pytest.mark.asyncio
    async def test_create_email_verification_token_user_not_found(
        self,
        auth_service: AuthService,
    ) -> None:
        """Test token creation fails when user not found."""
        # Arrange
        auth_service.user_repository.get_by_id = AsyncMock(return_value=None)

        # Act & Assert
        with pytest.raises(NotFoundError):
            await auth_service.create_email_verification_token("nonexistent-user")


class TestCleanupExpiredTokens:
    """Tests for AuthService.cleanup_expired_tokens method."""

    @pytest.mark.asyncio
    async def test_cleanup_expired_tokens_all_users(
        self,
        auth_service: AuthService,
        mock_session: AsyncMock,
    ) -> None:
        """Test cleanup of all expired tokens."""
        # Arrange
        mock_result = MagicMock()
        mock_result.rowcount = 5
        mock_session.execute.return_value = mock_result

        # Act
        deleted_count = await auth_service.cleanup_expired_tokens()

        # Assert
        assert deleted_count == 5
        mock_session.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_cleanup_expired_tokens_specific_user(
        self,
        auth_service: AuthService,
        mock_session: AsyncMock,
    ) -> None:
        """Test cleanup of expired tokens for specific user."""
        # Arrange
        mock_result = MagicMock()
        mock_result.rowcount = 2
        mock_session.execute.return_value = mock_result

        # Act
        deleted_count = await auth_service.cleanup_expired_tokens(user_id="user-123")

        # Assert
        assert deleted_count == 2
        mock_session.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_cleanup_expired_tokens_none_found(
        self,
        auth_service: AuthService,
        mock_session: AsyncMock,
    ) -> None:
        """Test cleanup when no expired tokens found."""
        # Arrange
        mock_result = MagicMock()
        mock_result.rowcount = 0
        mock_session.execute.return_value = mock_result

        # Act
        deleted_count = await auth_service.cleanup_expired_tokens()

        # Assert
        assert deleted_count == 0


class TestStoreRefreshToken:
    """Tests for AuthService._store_refresh_token method."""

    @pytest.mark.asyncio
    async def test_store_refresh_token_success(
        self,
        auth_service: AuthService,
        mock_session: AsyncMock,
    ) -> None:
        """Test storing refresh token in database."""
        # Act
        token = await auth_service._store_refresh_token("user-123", "new-refresh-token")

        # Assert
        mock_session.add.assert_called_once()
        mock_session.flush.assert_called_once()
        assert token.user_id == "user-123"
        assert token.token == "new-refresh-token"
        assert token.is_revoked is False
