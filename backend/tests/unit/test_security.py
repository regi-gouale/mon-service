"""
Unit tests for the security module.

Tests cover:
- Password hashing with bcrypt
- JWT token generation and validation
- Token expiration handling
"""

from datetime import timedelta

import jwt
import pytest

from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    get_password_hash,
    hash_password,
    verify_password,
)


class TestPasswordHashing:
    """Tests for password hashing functionality."""

    def test_get_password_hash_returns_hashed_string(self) -> None:
        """Test that get_password_hash returns a bcrypt hash string."""
        password = "SecurePassword123!"
        hashed = get_password_hash(password)

        assert hashed is not None
        assert isinstance(hashed, str)
        assert hashed != password
        # bcrypt hashes start with $2b$ or $2a$
        assert hashed.startswith("$2")

    def test_hash_password_alias_works(self) -> None:
        """Test that hash_password is an alias for get_password_hash."""
        password = "TestPassword456!"
        hashed = hash_password(password)

        assert hashed is not None
        assert isinstance(hashed, str)
        assert hashed.startswith("$2")

    def test_same_password_produces_different_hashes(self) -> None:
        """Test that the same password produces different hashes (salt)."""
        password = "SamePassword789!"
        hash1 = get_password_hash(password)
        hash2 = get_password_hash(password)

        assert hash1 != hash2

    def test_verify_password_correct(self) -> None:
        """Test that verify_password returns True for correct password."""
        password = "CorrectPassword123!"
        hashed = get_password_hash(password)

        assert verify_password(password, hashed) is True

    def test_verify_password_incorrect(self) -> None:
        """Test that verify_password returns False for incorrect password."""
        password = "CorrectPassword123!"
        wrong_password = "WrongPassword456!"
        hashed = get_password_hash(password)

        assert verify_password(wrong_password, hashed) is False

    def test_verify_password_empty_password(self) -> None:
        """Test password verification with empty password."""
        password = "RealPassword123!"
        hashed = get_password_hash(password)

        assert verify_password("", hashed) is False

    def test_hash_password_with_special_characters(self) -> None:
        """Test hashing passwords with special characters."""
        password = "P@$$w0rd!#$%^&*()"
        hashed = get_password_hash(password)

        assert verify_password(password, hashed) is True

    def test_hash_password_with_unicode(self) -> None:
        """Test hashing passwords with unicode characters."""
        password = "Пароль密码🔐"
        hashed = get_password_hash(password)

        assert verify_password(password, hashed) is True


class TestJWTAccessToken:
    """Tests for JWT access token functionality."""

    def test_create_access_token_returns_string(self) -> None:
        """Test that create_access_token returns a JWT string."""
        token = create_access_token(subject="user123")

        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0

    def test_create_access_token_with_int_subject(self) -> None:
        """Test creating access token with integer subject."""
        token = create_access_token(subject=42)

        decoded = decode_token(token)
        assert decoded["sub"] == "42"

    def test_create_access_token_contains_required_claims(self) -> None:
        """Test that access token contains required claims."""
        subject = "user456"
        token = create_access_token(subject=subject)
        decoded = decode_token(token)

        assert decoded["sub"] == subject
        assert decoded["type"] == "access"
        assert "exp" in decoded
        assert "iat" in decoded

    def test_create_access_token_with_extra_claims(self) -> None:
        """Test creating access token with extra claims."""
        subject = "user789"
        extra_claims = {"role": "admin", "org_id": "org123"}
        token = create_access_token(subject=subject, extra_claims=extra_claims)
        decoded = decode_token(token)

        assert decoded["sub"] == subject
        assert decoded["role"] == "admin"
        assert decoded["org_id"] == "org123"

    def test_create_access_token_with_custom_expiry(self) -> None:
        """Test creating access token with custom expiration."""
        subject = "user101"
        expires_delta = timedelta(hours=2)
        token = create_access_token(subject=subject, expires_delta=expires_delta)
        decoded = decode_token(token)

        assert decoded["sub"] == subject
        # Token should be valid (not expired)
        assert "exp" in decoded


class TestJWTRefreshToken:
    """Tests for JWT refresh token functionality."""

    def test_create_refresh_token_returns_string(self) -> None:
        """Test that create_refresh_token returns a JWT string."""
        token = create_refresh_token(subject="user123")

        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0

    def test_create_refresh_token_with_int_subject(self) -> None:
        """Test creating refresh token with integer subject."""
        token = create_refresh_token(subject=42)

        decoded = decode_token(token)
        assert decoded["sub"] == "42"

    def test_create_refresh_token_contains_required_claims(self) -> None:
        """Test that refresh token contains required claims."""
        subject = "user456"
        token = create_refresh_token(subject=subject)
        decoded = decode_token(token)

        assert decoded["sub"] == subject
        assert decoded["type"] == "refresh"
        assert "exp" in decoded
        assert "iat" in decoded

    def test_create_refresh_token_with_custom_expiry(self) -> None:
        """Test creating refresh token with custom expiration."""
        subject = "user101"
        expires_delta = timedelta(days=30)
        token = create_refresh_token(subject=subject, expires_delta=expires_delta)
        decoded = decode_token(token)

        assert decoded["sub"] == subject
        assert "exp" in decoded

    def test_access_and_refresh_tokens_are_different(self) -> None:
        """Test that access and refresh tokens for same subject are different."""
        subject = "user202"
        access_token = create_access_token(subject=subject)
        refresh_token = create_refresh_token(subject=subject)

        assert access_token != refresh_token

        access_decoded = decode_token(access_token)
        refresh_decoded = decode_token(refresh_token)

        assert access_decoded["type"] == "access"
        assert refresh_decoded["type"] == "refresh"


class TestDecodeToken:
    """Tests for JWT token decoding functionality."""

    def test_decode_valid_token(self) -> None:
        """Test decoding a valid token."""
        subject = "user303"
        token = create_access_token(subject=subject)
        decoded = decode_token(token)

        assert decoded["sub"] == subject
        assert decoded["type"] == "access"

    def test_decode_expired_token_raises_error(self) -> None:
        """Test that decoding an expired token raises an error."""
        subject = "user404"
        # Create token that expires immediately
        expires_delta = timedelta(seconds=-1)
        token = create_access_token(subject=subject, expires_delta=expires_delta)

        with pytest.raises(jwt.ExpiredSignatureError):
            decode_token(token)

    def test_decode_invalid_token_raises_error(self) -> None:
        """Test that decoding an invalid token raises an error."""
        invalid_token = "invalid.token.string"

        with pytest.raises(jwt.InvalidTokenError):
            decode_token(invalid_token)

    def test_decode_tampered_token_raises_error(self) -> None:
        """Test that decoding a tampered token raises an error."""
        token = create_access_token(subject="user505")
        # Tamper with the token by modifying a character
        tampered_token = token[:-5] + "XXXXX"

        with pytest.raises(jwt.InvalidTokenError):
            decode_token(tampered_token)

    def test_decode_token_with_wrong_signature_fails(self) -> None:
        """Test that token with wrong signature fails."""
        # This test verifies the signature is checked
        subject = "user606"
        token = create_access_token(subject=subject)

        # Try to decode with different signature by tampering
        # The token signature won't match
        parts = token.split(".")
        if len(parts) == 3:
            # Modify signature
            tampered = parts[0] + "." + parts[1] + ".tampered_signature"
            with pytest.raises(jwt.InvalidTokenError):
                decode_token(tampered)


class TestTokenTypeValidation:
    """Tests for validating token types."""

    def test_access_token_has_correct_type(self) -> None:
        """Test that access token has type 'access'."""
        token = create_access_token(subject="user707")
        decoded = decode_token(token)

        assert decoded["type"] == "access"

    def test_refresh_token_has_correct_type(self) -> None:
        """Test that refresh token has type 'refresh'."""
        token = create_refresh_token(subject="user808")
        decoded = decode_token(token)

        assert decoded["type"] == "refresh"


class TestEdgeCases:
    """Edge case tests for security module."""

    def test_password_at_bcrypt_limit(self) -> None:
        """Test hashing a password at bcrypt's 72-byte limit."""
        # bcrypt has a 72-byte limit
        password_72_bytes = "A" * 72
        hashed = get_password_hash(password_72_bytes)

        assert verify_password(password_72_bytes, hashed) is True

    def test_empty_subject_in_token(self) -> None:
        """Test creating token with empty subject."""
        token = create_access_token(subject="")
        decoded = decode_token(token)

        assert decoded["sub"] == ""

    def test_special_characters_in_subject(self) -> None:
        """Test token with special characters in subject."""
        subject = "user@example.com"
        token = create_access_token(subject=subject)
        decoded = decode_token(token)

        assert decoded["sub"] == subject

    def test_uuid_as_subject(self) -> None:
        """Test token with UUID as subject."""
        import uuid

        subject = str(uuid.uuid4())
        token = create_access_token(subject=subject)
        decoded = decode_token(token)

        assert decoded["sub"] == subject

    def test_extra_claims_are_included_in_token(self) -> None:
        """Test that extra claims are included in the token."""
        subject = "original_user"
        extra_claims = {"role": "admin", "permissions": ["read", "write"]}
        token = create_access_token(subject=subject, extra_claims=extra_claims)
        decoded = decode_token(token)

        # Extra claims should be present
        assert decoded["role"] == "admin"
        assert decoded["permissions"] == ["read", "write"]
        # Required claims should still be present
        assert decoded["sub"] == subject
        assert decoded["type"] == "access"
