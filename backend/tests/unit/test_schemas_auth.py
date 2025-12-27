"""
Unit tests for the authentication schemas.

Tests cover:
- RegisterRequest validation (email, password strength, names)
- LoginRequest validation
- TokenPayload structure
- RefreshTokenRequest validation
- AuthResponse structure
"""

from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from app.schemas.auth import (
    AuthResponse,
    ForgotPasswordRequest,
    LoginRequest,
    MessageResponse,
    RefreshTokenRequest,
    RegisterRequest,
    ResetPasswordRequest,
    TokenPayload,
    UserResponse,
    VerifyEmailRequest,
)


class TestRegisterRequest:
    """Tests for RegisterRequest schema."""

    def test_valid_registration(self) -> None:
        """Test valid registration data."""
        data = {
            "email": "user@example.com",
            "password": "SecureP@ss123",
            "first_name": "John",
            "last_name": "Doe",
        }
        request = RegisterRequest(**data)

        assert request.email == "user@example.com"
        assert request.password == "SecureP@ss123"
        assert request.first_name == "John"
        assert request.last_name == "Doe"

    def test_invalid_email_format(self) -> None:
        """Test that invalid email format raises error."""
        data = {
            "email": "invalid-email",
            "password": "SecureP@ss123",
            "first_name": "John",
            "last_name": "Doe",
        }
        with pytest.raises(ValidationError) as exc_info:
            RegisterRequest(**data)

        errors = exc_info.value.errors()
        assert any(e["loc"] == ("email",) for e in errors)

    def test_password_too_short(self) -> None:
        """Test that password shorter than 8 chars raises error."""
        data = {
            "email": "user@example.com",
            "password": "Short1!",
            "first_name": "John",
            "last_name": "Doe",
        }
        with pytest.raises(ValidationError) as exc_info:
            RegisterRequest(**data)

        errors = exc_info.value.errors()
        assert any(e["loc"] == ("password",) for e in errors)

    def test_password_missing_uppercase(self) -> None:
        """Test that password without uppercase raises error."""
        data = {
            "email": "user@example.com",
            "password": "nouppercase123!",
            "first_name": "John",
            "last_name": "Doe",
        }
        with pytest.raises(ValidationError) as exc_info:
            RegisterRequest(**data)

        errors = exc_info.value.errors()
        assert any("uppercase" in str(e["msg"]).lower() for e in errors)

    def test_password_missing_lowercase(self) -> None:
        """Test that password without lowercase raises error."""
        data = {
            "email": "user@example.com",
            "password": "NOLOWERCASE123!",
            "first_name": "John",
            "last_name": "Doe",
        }
        with pytest.raises(ValidationError) as exc_info:
            RegisterRequest(**data)

        errors = exc_info.value.errors()
        assert any("lowercase" in str(e["msg"]).lower() for e in errors)

    def test_password_missing_digit(self) -> None:
        """Test that password without digit raises error."""
        data = {
            "email": "user@example.com",
            "password": "NoDigitsHere!@",
            "first_name": "John",
            "last_name": "Doe",
        }
        with pytest.raises(ValidationError) as exc_info:
            RegisterRequest(**data)

        errors = exc_info.value.errors()
        assert any("digit" in str(e["msg"]).lower() for e in errors)

    def test_password_missing_special_char(self) -> None:
        """Test that password without special char raises error."""
        data = {
            "email": "user@example.com",
            "password": "NoSpecial123",
            "first_name": "John",
            "last_name": "Doe",
        }
        with pytest.raises(ValidationError) as exc_info:
            RegisterRequest(**data)

        errors = exc_info.value.errors()
        assert any("special" in str(e["msg"]).lower() for e in errors)

    def test_password_with_various_special_chars(self) -> None:
        """Test password validation with various special characters."""
        special_chars = ["!", "@", "#", "$", "%", "^", "&", "*", "(", ")", "_", "-"]
        for char in special_chars:
            data = {
                "email": "user@example.com",
                "password": f"Password1{char}",
                "first_name": "John",
                "last_name": "Doe",
            }
            request = RegisterRequest(**data)
            assert request.password == f"Password1{char}"

    def test_empty_first_name(self) -> None:
        """Test that empty first name raises error."""
        data = {
            "email": "user@example.com",
            "password": "SecureP@ss123",
            "first_name": "",
            "last_name": "Doe",
        }
        with pytest.raises(ValidationError) as exc_info:
            RegisterRequest(**data)

        errors = exc_info.value.errors()
        assert any(e["loc"] == ("first_name",) for e in errors)

    def test_whitespace_only_name(self) -> None:
        """Test that whitespace-only name raises error."""
        data = {
            "email": "user@example.com",
            "password": "SecureP@ss123",
            "first_name": "   ",
            "last_name": "Doe",
        }
        with pytest.raises(ValidationError) as exc_info:
            RegisterRequest(**data)

        errors = exc_info.value.errors()
        assert any(e["loc"] == ("first_name",) for e in errors)

    def test_name_stripping(self) -> None:
        """Test that names are stripped of whitespace."""
        data = {
            "email": "user@example.com",
            "password": "SecureP@ss123",
            "first_name": "  John  ",
            "last_name": "  Doe  ",
        }
        request = RegisterRequest(**data)

        assert request.first_name == "John"
        assert request.last_name == "Doe"

    def test_first_name_too_long(self) -> None:
        """Test that first name exceeding max length raises error."""
        data = {
            "email": "user@example.com",
            "password": "SecureP@ss123",
            "first_name": "A" * 101,
            "last_name": "Doe",
        }
        with pytest.raises(ValidationError) as exc_info:
            RegisterRequest(**data)

        errors = exc_info.value.errors()
        assert any(e["loc"] == ("first_name",) for e in errors)

    def test_missing_required_field(self) -> None:
        """Test that missing required field raises error."""
        data = {
            "email": "user@example.com",
            "password": "SecureP@ss123",
            "first_name": "John",
            # missing last_name
        }
        with pytest.raises(ValidationError) as exc_info:
            RegisterRequest(**data)

        errors = exc_info.value.errors()
        # Pydantic uses the alias in error location when field is missing
        assert any(e["loc"] == ("lastName",) for e in errors)


class TestLoginRequest:
    """Tests for LoginRequest schema."""

    def test_valid_login(self) -> None:
        """Test valid login data."""
        data = {
            "email": "user@example.com",
            "password": "anypassword",
        }
        request = LoginRequest(**data)

        assert request.email == "user@example.com"
        assert request.password == "anypassword"

    def test_invalid_email(self) -> None:
        """Test that invalid email raises error."""
        data = {
            "email": "not-an-email",
            "password": "password",
        }
        with pytest.raises(ValidationError) as exc_info:
            LoginRequest(**data)

        errors = exc_info.value.errors()
        assert any(e["loc"] == ("email",) for e in errors)

    def test_empty_password(self) -> None:
        """Test that empty password raises error."""
        data = {
            "email": "user@example.com",
            "password": "",
        }
        with pytest.raises(ValidationError) as exc_info:
            LoginRequest(**data)

        errors = exc_info.value.errors()
        assert any(e["loc"] == ("password",) for e in errors)

    def test_missing_email(self) -> None:
        """Test that missing email raises error."""
        data = {"password": "password"}
        with pytest.raises(ValidationError) as exc_info:
            LoginRequest(**data)

        errors = exc_info.value.errors()
        assert any(e["loc"] == ("email",) for e in errors)


class TestTokenPayload:
    """Tests for TokenPayload schema."""

    def test_access_token_payload(self) -> None:
        """Test valid access token payload."""
        now = datetime.now(UTC)
        data = {
            "sub": "user-123",
            "exp": now,
            "iat": now,
            "type": "access",
        }
        payload = TokenPayload(**data)

        assert payload.sub == "user-123"
        assert payload.exp == now
        assert payload.iat == now
        assert payload.type == "access"

    def test_refresh_token_payload(self) -> None:
        """Test valid refresh token payload."""
        now = datetime.now(UTC)
        data = {
            "sub": "user-456",
            "exp": now,
            "type": "refresh",
        }
        payload = TokenPayload(**data)

        assert payload.sub == "user-456"
        assert payload.type == "refresh"
        assert payload.iat is None  # optional field

    def test_invalid_token_type(self) -> None:
        """Test that invalid token type raises error."""
        now = datetime.now(UTC)
        data = {
            "sub": "user-123",
            "exp": now,
            "type": "invalid",
        }
        with pytest.raises(ValidationError) as exc_info:
            TokenPayload(**data)

        errors = exc_info.value.errors()
        assert any(e["loc"] == ("type",) for e in errors)

    def test_missing_required_fields(self) -> None:
        """Test that missing required fields raise error."""
        with pytest.raises(ValidationError):
            TokenPayload(sub="user-123")  # type: ignore[call-arg]


class TestRefreshTokenRequest:
    """Tests for RefreshTokenRequest schema."""

    def test_valid_refresh_request(self) -> None:
        """Test valid refresh token request."""
        data = {"refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."}
        request = RefreshTokenRequest(**data)

        assert request.refresh_token == "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

    def test_empty_refresh_token(self) -> None:
        """Test that empty refresh token raises error."""
        data = {"refresh_token": ""}
        with pytest.raises(ValidationError) as exc_info:
            RefreshTokenRequest(**data)

        errors = exc_info.value.errors()
        assert any(e["loc"] == ("refresh_token",) for e in errors)

    def test_missing_refresh_token(self) -> None:
        """Test that missing refresh token raises error."""
        with pytest.raises(ValidationError):
            RefreshTokenRequest()  # type: ignore[call-arg]


class TestUserResponse:
    """Tests for UserResponse schema."""

    def test_valid_user_response(self) -> None:
        """Test valid user response."""
        now = datetime.now(UTC)
        data = {
            "id": "user-123",
            "email": "user@example.com",
            "first_name": "John",
            "last_name": "Doe",
            "role": "member",
            "email_verified": True,
            "avatar_url": "https://example.com/avatar.jpg",
            "created_at": now,
        }
        user = UserResponse(**data)

        assert user.id == "user-123"
        assert user.email == "user@example.com"
        assert user.first_name == "John"
        assert user.last_name == "Doe"
        assert user.role == "member"
        assert user.email_verified is True
        assert user.avatar_url == "https://example.com/avatar.jpg"
        assert user.created_at == now

    def test_user_response_optional_fields(self) -> None:
        """Test user response with optional fields as None."""
        now = datetime.now(UTC)
        data = {
            "id": "user-123",
            "email": "user@example.com",
            "first_name": "John",
            "last_name": "Doe",
            "role": "member",
            "created_at": now,
        }
        user = UserResponse(**data)

        assert user.email_verified is False  # default
        assert user.avatar_url is None  # default


class TestAuthResponse:
    """Tests for AuthResponse schema."""

    def test_valid_auth_response(self) -> None:
        """Test valid auth response."""
        now = datetime.now(UTC)
        data = {
            "access_token": "access_token_value",
            "refresh_token": "refresh_token_value",
            "user": {
                "id": "user-123",
                "email": "user@example.com",
                "first_name": "John",
                "last_name": "Doe",
                "role": "member",
                "created_at": now,
            },
        }
        response = AuthResponse(**data)

        assert response.access_token == "access_token_value"
        assert response.refresh_token == "refresh_token_value"
        assert response.token_type == "bearer"  # default
        assert response.user.id == "user-123"
        assert response.user.email == "user@example.com"

    def test_auth_response_token_type(self) -> None:
        """Test that token_type is always bearer."""
        now = datetime.now(UTC)
        data = {
            "access_token": "access",
            "refresh_token": "refresh",
            "token_type": "bearer",
            "user": {
                "id": "user-123",
                "email": "user@example.com",
                "first_name": "John",
                "last_name": "Doe",
                "role": "member",
                "created_at": now,
            },
        }
        response = AuthResponse(**data)
        assert response.token_type == "bearer"


class TestForgotPasswordRequest:
    """Tests for ForgotPasswordRequest schema."""

    def test_valid_forgot_password(self) -> None:
        """Test valid forgot password request."""
        data = {"email": "user@example.com"}
        request = ForgotPasswordRequest(**data)

        assert request.email == "user@example.com"

    def test_invalid_email(self) -> None:
        """Test that invalid email raises error."""
        data = {"email": "not-an-email"}
        with pytest.raises(ValidationError) as exc_info:
            ForgotPasswordRequest(**data)

        errors = exc_info.value.errors()
        assert any(e["loc"] == ("email",) for e in errors)


class TestResetPasswordRequest:
    """Tests for ResetPasswordRequest schema."""

    def test_valid_reset_password(self) -> None:
        """Test valid reset password request."""
        data = {
            "token": "reset-token-123",
            "password": "NewSecureP@ss123",
        }
        request = ResetPasswordRequest(**data)

        assert request.token == "reset-token-123"
        assert request.password == "NewSecureP@ss123"

    def test_password_validation(self) -> None:
        """Test that password validation is applied."""
        data = {
            "token": "reset-token-123",
            "password": "weak",
        }
        with pytest.raises(ValidationError):
            ResetPasswordRequest(**data)

    def test_empty_token(self) -> None:
        """Test that empty token raises error."""
        data = {
            "token": "",
            "password": "NewSecureP@ss123",
        }
        with pytest.raises(ValidationError) as exc_info:
            ResetPasswordRequest(**data)

        errors = exc_info.value.errors()
        assert any(e["loc"] == ("token",) for e in errors)


class TestVerifyEmailRequest:
    """Tests for VerifyEmailRequest schema."""

    def test_valid_verify_email(self) -> None:
        """Test valid verify email request."""
        data = {"token": "verification-token-123"}
        request = VerifyEmailRequest(**data)

        assert request.token == "verification-token-123"

    def test_empty_token(self) -> None:
        """Test that empty token raises error."""
        data = {"token": ""}
        with pytest.raises(ValidationError) as exc_info:
            VerifyEmailRequest(**data)

        errors = exc_info.value.errors()
        assert any(e["loc"] == ("token",) for e in errors)


class TestMessageResponse:
    """Tests for MessageResponse schema."""

    def test_valid_message_response(self) -> None:
        """Test valid message response."""
        data = {"message": "Operation successful"}
        response = MessageResponse(**data)

        assert response.message == "Operation successful"

    def test_missing_message(self) -> None:
        """Test that missing message raises error."""
        with pytest.raises(ValidationError):
            MessageResponse()  # type: ignore[call-arg]
