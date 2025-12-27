"""
Integration Tests for Auth API Routes.

Tests for authentication endpoints including registration,
login, token refresh, logout, and password reset.
"""

from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock, patch

import jwt
import pytest
from fastapi import status
from httpx import ASGITransport, AsyncClient

from app.core.config import settings
from app.core.exceptions import AlreadyExistsError, NotFoundError, UnauthorizedError
from app.main import app
from app.models.user import User, UserRole
from app.schemas.auth import AuthResponse, UserResponse


@pytest.fixture
def sample_user() -> User:
    """Create a sample user for testing."""
    return User(
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


@pytest.fixture
def sample_auth_response(sample_user: User) -> AuthResponse:
    """Create a sample auth response."""
    return AuthResponse(
        access_token="access-token-123",
        refresh_token="refresh-token-123",
        token_type="bearer",
        user=UserResponse(
            id=sample_user.id,
            email=sample_user.email,
            first_name=sample_user.first_name,
            last_name=sample_user.last_name,
            role=sample_user.role.value,
            email_verified=sample_user.email_verified,
            avatar_url=sample_user.avatar_url,
            created_at=sample_user.created_at,
        ),
    )


@pytest.fixture
async def async_client() -> AsyncClient:
    """Create an async HTTP client for testing."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


class TestRegisterEndpoint:
    """Tests for POST /api/v1/auth/register."""

    @pytest.mark.asyncio
    async def test_register_success(
        self,
        async_client: AsyncClient,
        sample_auth_response: AuthResponse,
    ) -> None:
        """Test successful user registration."""
        with patch(
            "app.api.v1.routes.auth.AuthService.register",
            new_callable=AsyncMock,
            return_value=sample_auth_response,
        ):
            response = await async_client.post(
                "/api/v1/auth/register",
                json={
                    "email": "new@example.com",
                    "password": "SecureP@ss123",
                    "first_name": "New",
                    "last_name": "User",
                },
            )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert "accessToken" in data
        assert "refreshToken" in data
        assert data["tokenType"] == "bearer"
        assert "user" in data

    @pytest.mark.asyncio
    async def test_register_email_already_exists(
        self,
        async_client: AsyncClient,
    ) -> None:
        """Test registration fails when email exists."""
        with patch(
            "app.api.v1.routes.auth.AuthService.register",
            new_callable=AsyncMock,
            side_effect=AlreadyExistsError(
                resource="User", field="email", value="existing@example.com"
            ),
        ):
            response = await async_client.post(
                "/api/v1/auth/register",
                json={
                    "email": "existing@example.com",
                    "password": "SecureP@ss123",
                    "first_name": "Test",
                    "last_name": "User",
                },
            )

        assert response.status_code == status.HTTP_409_CONFLICT

    @pytest.mark.asyncio
    async def test_register_weak_password(
        self,
        async_client: AsyncClient,
    ) -> None:
        """Test registration fails with weak password."""
        response = await async_client.post(
            "/api/v1/auth/register",
            json={
                "email": "new@example.com",
                "password": "weak",
                "first_name": "Test",
                "last_name": "User",
            },
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    @pytest.mark.asyncio
    async def test_register_invalid_email(
        self,
        async_client: AsyncClient,
    ) -> None:
        """Test registration fails with invalid email."""
        response = await async_client.post(
            "/api/v1/auth/register",
            json={
                "email": "not-an-email",
                "password": "SecureP@ss123",
                "first_name": "Test",
                "last_name": "User",
            },
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestLoginEndpoint:
    """Tests for POST /api/v1/auth/login."""

    @pytest.mark.asyncio
    async def test_login_success(
        self,
        async_client: AsyncClient,
        sample_auth_response: AuthResponse,
    ) -> None:
        """Test successful login."""
        with patch(
            "app.api.v1.routes.auth.AuthService.login",
            new_callable=AsyncMock,
            return_value=sample_auth_response,
        ):
            response = await async_client.post(
                "/api/v1/auth/login",
                json={
                    "email": "test@example.com",
                    "password": "ValidP@ss123",
                },
            )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "accessToken" in data
        assert "refreshToken" in data
        assert data["tokenType"] == "bearer"

    @pytest.mark.asyncio
    async def test_login_invalid_credentials(
        self,
        async_client: AsyncClient,
    ) -> None:
        """Test login fails with invalid credentials."""
        with patch(
            "app.api.v1.routes.auth.AuthService.login",
            new_callable=AsyncMock,
            side_effect=UnauthorizedError(message="Invalid email or password"),
        ):
            response = await async_client.post(
                "/api/v1/auth/login",
                json={
                    "email": "test@example.com",
                    "password": "WrongPassword!",
                },
            )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "WWW-Authenticate" in response.headers

    @pytest.mark.asyncio
    async def test_login_missing_fields(
        self,
        async_client: AsyncClient,
    ) -> None:
        """Test login fails with missing fields."""
        response = await async_client.post(
            "/api/v1/auth/login",
            json={"email": "test@example.com"},
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestRefreshEndpoint:
    """Tests for POST /api/v1/auth/refresh."""

    @pytest.mark.asyncio
    async def test_refresh_success(
        self,
        async_client: AsyncClient,
        sample_auth_response: AuthResponse,
    ) -> None:
        """Test successful token refresh."""
        with patch(
            "app.api.v1.routes.auth.AuthService.refresh_token",
            new_callable=AsyncMock,
            return_value=sample_auth_response,
        ):
            response = await async_client.post(
                "/api/v1/auth/refresh",
                json={"refresh_token": "valid-refresh-token"},
            )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "accessToken" in data
        assert "refreshToken" in data

    @pytest.mark.asyncio
    async def test_refresh_expired_token(
        self,
        async_client: AsyncClient,
    ) -> None:
        """Test refresh fails with expired token."""
        with patch(
            "app.api.v1.routes.auth.AuthService.refresh_token",
            new_callable=AsyncMock,
            side_effect=UnauthorizedError(message="Refresh token has expired"),
        ):
            response = await async_client.post(
                "/api/v1/auth/refresh",
                json={"refresh_token": "expired-token"},
            )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.asyncio
    async def test_refresh_invalid_token(
        self,
        async_client: AsyncClient,
    ) -> None:
        """Test refresh fails with invalid token."""
        with patch(
            "app.api.v1.routes.auth.AuthService.refresh_token",
            new_callable=AsyncMock,
            side_effect=UnauthorizedError(message="Invalid refresh token"),
        ):
            response = await async_client.post(
                "/api/v1/auth/refresh",
                json={"refresh_token": "invalid-token"},
            )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestLogoutEndpoint:
    """Tests for POST /api/v1/auth/logout."""

    @pytest.mark.asyncio
    async def test_logout_success(
        self,
        async_client: AsyncClient,
        sample_user: User,
    ) -> None:
        """Test successful logout."""
        # Create a valid refresh token
        valid_token = jwt.encode(
            {
                "sub": sample_user.id,
                "type": "refresh",
                "exp": datetime.now(UTC) + timedelta(days=7),
            },
            settings.secret_key,
            algorithm=settings.jwt_algorithm,
        )

        with patch(
            "app.api.v1.routes.auth.AuthService.logout",
            new_callable=AsyncMock,
        ):
            response = await async_client.post(
                "/api/v1/auth/logout",
                json={"refresh_token": valid_token},
            )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["message"] == "Successfully logged out"

    @pytest.mark.asyncio
    async def test_logout_invalid_token(
        self,
        async_client: AsyncClient,
    ) -> None:
        """Test logout fails with invalid token."""
        response = await async_client.post(
            "/api/v1/auth/logout",
            json={"refresh_token": "invalid-token"},
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.asyncio
    async def test_logout_token_not_found(
        self,
        async_client: AsyncClient,
        sample_user: User,
    ) -> None:
        """Test logout fails when token not in database."""
        valid_token = jwt.encode(
            {
                "sub": sample_user.id,
                "type": "refresh",
                "exp": datetime.now(UTC) + timedelta(days=7),
            },
            settings.secret_key,
            algorithm=settings.jwt_algorithm,
        )

        with patch(
            "app.api.v1.routes.auth.AuthService.logout",
            new_callable=AsyncMock,
            side_effect=NotFoundError(resource="RefreshToken"),
        ):
            response = await async_client.post(
                "/api/v1/auth/logout",
                json={"refresh_token": valid_token},
            )

        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestForgotPasswordEndpoint:
    """Tests for POST /api/v1/auth/forgot-password."""

    @pytest.mark.asyncio
    async def test_forgot_password_success(
        self,
        async_client: AsyncClient,
    ) -> None:
        """Test forgot password returns success for existing email."""
        with patch(
            "app.api.v1.routes.auth.AuthService.forgot_password",
            new_callable=AsyncMock,
            return_value="reset-token-123",
        ):
            response = await async_client.post(
                "/api/v1/auth/forgot-password",
                json={"email": "existing@example.com"},
            )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "message" in data

    @pytest.mark.asyncio
    async def test_forgot_password_unknown_email(
        self,
        async_client: AsyncClient,
    ) -> None:
        """Test forgot password returns success for unknown email (security)."""
        with patch(
            "app.api.v1.routes.auth.AuthService.forgot_password",
            new_callable=AsyncMock,
            side_effect=NotFoundError(resource="User"),
        ):
            response = await async_client.post(
                "/api/v1/auth/forgot-password",
                json={"email": "unknown@example.com"},
            )

        # Should still return 200 to prevent email enumeration
        assert response.status_code == status.HTTP_200_OK

    @pytest.mark.asyncio
    async def test_forgot_password_invalid_email(
        self,
        async_client: AsyncClient,
    ) -> None:
        """Test forgot password fails with invalid email format."""
        response = await async_client.post(
            "/api/v1/auth/forgot-password",
            json={"email": "not-an-email"},
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestResetPasswordEndpoint:
    """Tests for POST /api/v1/auth/reset-password."""

    @pytest.mark.asyncio
    async def test_reset_password_success(
        self,
        async_client: AsyncClient,
    ) -> None:
        """Test successful password reset."""
        with patch(
            "app.api.v1.routes.auth.AuthService.reset_password",
            new_callable=AsyncMock,
        ):
            response = await async_client.post(
                "/api/v1/auth/reset-password",
                json={
                    "token": "valid-reset-token",
                    "password": "NewSecureP@ss456",
                },
            )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "successfully" in data["message"].lower()

    @pytest.mark.asyncio
    async def test_reset_password_expired_token(
        self,
        async_client: AsyncClient,
    ) -> None:
        """Test reset password fails with expired token."""
        with patch(
            "app.api.v1.routes.auth.AuthService.reset_password",
            new_callable=AsyncMock,
            side_effect=UnauthorizedError(message="Reset token has expired"),
        ):
            response = await async_client.post(
                "/api/v1/auth/reset-password",
                json={
                    "token": "expired-token",
                    "password": "NewSecureP@ss456",
                },
            )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.asyncio
    async def test_reset_password_weak_password(
        self,
        async_client: AsyncClient,
    ) -> None:
        """Test reset password fails with weak password."""
        response = await async_client.post(
            "/api/v1/auth/reset-password",
            json={
                "token": "valid-token",
                "password": "weak",
            },
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestVerifyEmailEndpoint:
    """Tests for POST /api/v1/auth/verify-email."""

    @pytest.mark.asyncio
    async def test_verify_email_success(
        self,
        async_client: AsyncClient,
    ) -> None:
        """Test successful email verification."""
        with patch(
            "app.api.v1.routes.auth.AuthService.verify_email",
            new_callable=AsyncMock,
        ):
            response = await async_client.post(
                "/api/v1/auth/verify-email",
                json={"token": "valid-verification-token"},
            )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "verified" in data["message"].lower()

    @pytest.mark.asyncio
    async def test_verify_email_invalid_token(
        self,
        async_client: AsyncClient,
    ) -> None:
        """Test email verification fails with invalid token."""
        with patch(
            "app.api.v1.routes.auth.AuthService.verify_email",
            new_callable=AsyncMock,
            side_effect=UnauthorizedError(message="Invalid verification token"),
        ):
            response = await async_client.post(
                "/api/v1/auth/verify-email",
                json={"token": "invalid-token"},
            )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.asyncio
    async def test_verify_email_expired_token(
        self,
        async_client: AsyncClient,
    ) -> None:
        """Test email verification fails with expired token."""
        with patch(
            "app.api.v1.routes.auth.AuthService.verify_email",
            new_callable=AsyncMock,
            side_effect=UnauthorizedError(message="Verification token has expired"),
        ):
            response = await async_client.post(
                "/api/v1/auth/verify-email",
                json={"token": "expired-token"},
            )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestOpenAPIDocumentation:
    """Tests for OpenAPI documentation."""

    @pytest.mark.asyncio
    async def test_openapi_schema_available(
        self,
        async_client: AsyncClient,
    ) -> None:
        """Test that OpenAPI schema is available."""
        response = await async_client.get("/openapi.json")
        assert response.status_code == status.HTTP_200_OK

        schema = response.json()
        assert "paths" in schema

        # Check auth endpoints are documented
        auth_paths = [p for p in schema["paths"] if "/auth/" in p]
        assert len(auth_paths) >= 6  # At least 6 auth endpoints

    @pytest.mark.asyncio
    async def test_auth_endpoints_in_openapi(
        self,
        async_client: AsyncClient,
    ) -> None:
        """Test that all auth endpoints are in OpenAPI schema."""
        response = await async_client.get("/openapi.json")
        schema = response.json()

        expected_endpoints = [
            "/api/v1/auth/register",
            "/api/v1/auth/login",
            "/api/v1/auth/refresh",
            "/api/v1/auth/logout",
            "/api/v1/auth/forgot-password",
            "/api/v1/auth/reset-password",
        ]

        for endpoint in expected_endpoints:
            assert endpoint in schema["paths"], f"Missing endpoint: {endpoint}"
            assert "post" in schema["paths"][endpoint], f"Missing POST for {endpoint}"
