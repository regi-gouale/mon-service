"""
Authentication Schemas.

Pydantic schemas for authentication request/response validation.
Includes registration, login, token management, and user data schemas.
"""

import re
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, EmailStr, Field, field_validator


class RegisterRequest(BaseModel):
    """
    Schema for user registration request.

    Attributes:
        email: User's email address (validated format)
        password: User's password (min 8 chars, complexity required)
        first_name: User's first name
        last_name: User's last name
    """

    model_config = {"populate_by_name": True}

    email: EmailStr = Field(
        ...,
        description="User's email address",
        examples=["user@example.com"],
    )
    password: str = Field(
        ...,
        min_length=8,
        max_length=128,
        description="User's password (min 8 characters)",
        examples=["SecureP@ss123"],
    )
    first_name: str = Field(
        ...,
        alias="firstName",
        min_length=1,
        max_length=100,
        description="User's first name",
        examples=["John"],
    )
    last_name: str = Field(
        ...,
        alias="lastName",
        min_length=1,
        max_length=100,
        description="User's last name",
        examples=["Doe"],
    )

    @field_validator("password", mode="after")
    @classmethod
    def validate_password_strength(cls, password: str) -> str:
        """
        Validate password meets security requirements.

        Requirements:
        - At least 8 characters (enforced by min_length)
        - At least one uppercase letter
        - At least one lowercase letter
        - At least one digit
        - At least one special character
        """
        if not any(c.isupper() for c in password):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.islower() for c in password):
            raise ValueError("Password must contain at least one lowercase letter")
        if not any(c.isdigit() for c in password):
            raise ValueError("Password must contain at least one digit")
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>_\-+=\[\]\\;'/`~]", password):
            raise ValueError("Password must contain at least one special character")
        return password

    @field_validator("first_name", "last_name", mode="after")
    @classmethod
    def validate_name(cls, name: str) -> str:
        """Validate and normalize name fields."""
        # Strip whitespace and validate
        name = name.strip()
        if not name:
            raise ValueError("Name cannot be empty or whitespace only")
        return name


class LoginRequest(BaseModel):
    """
    Schema for user login request.

    Attributes:
        email: User's email address
        password: User's password
    """

    email: EmailStr = Field(
        ...,
        description="User's email address",
        examples=["user@example.com"],
    )
    password: str = Field(
        ...,
        min_length=1,
        description="User's password",
        examples=["SecureP@ss123"],
    )


class TokenPayload(BaseModel):
    """
    Schema for JWT token payload.

    Attributes:
        sub: Subject (user ID)
        exp: Expiration timestamp
        iat: Issued at timestamp
        type: Token type (access or refresh)
    """

    sub: str = Field(
        ...,
        description="Subject - typically the user ID",
    )
    exp: datetime = Field(
        ...,
        description="Token expiration timestamp",
    )
    iat: datetime | None = Field(
        default=None,
        description="Token issued at timestamp",
    )
    type: Literal["access", "refresh"] = Field(
        ...,
        description="Token type",
    )


class RefreshTokenRequest(BaseModel):
    """
    Schema for refresh token request.

    Attributes:
        refresh_token: The refresh token to exchange for new tokens
    """

    refresh_token: str = Field(
        ...,
        min_length=1,
        description="The refresh token",
    )


class UserResponse(BaseModel):
    """
    Schema for user data in responses.

    Attributes:
        id: User's unique identifier
        email: User's email address
        first_name: User's first name
        last_name: User's last name
        role: User's role
        organization_id: User's organization ID
        email_verified: Whether email is verified
        avatar_url: URL to user's avatar (optional)
        created_at: Account creation timestamp
    """

    model_config = {"from_attributes": True, "populate_by_name": True}

    id: str = Field(
        ...,
        description="User's unique identifier",
    )
    email: EmailStr = Field(
        ...,
        description="User's email address",
    )
    first_name: str = Field(
        ...,
        serialization_alias="firstName",
        description="User's first name",
    )
    last_name: str = Field(
        ...,
        serialization_alias="lastName",
        description="User's last name",
    )
    role: str = Field(
        ...,
        description="User's role (admin, manager, member, guest)",
    )
    organization_id: str | None = Field(
        default=None,
        serialization_alias="organizationId",
        description="User's organization ID",
    )
    email_verified: bool = Field(
        default=False,
        serialization_alias="isEmailVerified",
        description="Whether the user's email is verified",
    )
    avatar_url: str | None = Field(
        default=None,
        serialization_alias="avatarUrl",
        description="URL to user's avatar image",
    )
    created_at: datetime = Field(
        ...,
        serialization_alias="createdAt",
        description="Account creation timestamp",
    )


class AuthResponse(BaseModel):
    """
    Schema for authentication response.

    Returned after successful login or token refresh.

    Attributes:
        access_token: JWT access token
        refresh_token: JWT refresh token
        token_type: Token type (always "bearer")
        user: User data
    """

    model_config = {"populate_by_name": True}

    access_token: str = Field(
        ...,
        serialization_alias="accessToken",
        description="JWT access token",
    )
    refresh_token: str = Field(
        ...,
        serialization_alias="refreshToken",
        description="JWT refresh token",
    )
    token_type: Literal["bearer"] = Field(
        default="bearer",
        serialization_alias="tokenType",
        description="Token type",
    )
    user: UserResponse = Field(
        ...,
        description="Authenticated user data",
    )


class ForgotPasswordRequest(BaseModel):
    """
    Schema for forgot password request.

    Attributes:
        email: User's email address to send reset link
    """

    email: EmailStr = Field(
        ...,
        description="User's email address",
        examples=["user@example.com"],
    )


class ResetPasswordRequest(BaseModel):
    """
    Schema for password reset request.

    Attributes:
        token: Password reset token
        password: New password
    """

    token: str = Field(
        ...,
        min_length=1,
        description="Password reset token",
    )
    password: str = Field(
        ...,
        min_length=8,
        max_length=128,
        description="New password (min 8 characters)",
        examples=["NewSecureP@ss123"],
    )

    @field_validator("password", mode="after")
    @classmethod
    def validate_password_strength(cls, password: str) -> str:
        """
        Validate password meets security requirements.

        Same requirements as RegisterRequest.
        """
        if not any(c.isupper() for c in password):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.islower() for c in password):
            raise ValueError("Password must contain at least one lowercase letter")
        if not any(c.isdigit() for c in password):
            raise ValueError("Password must contain at least one digit")
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>_\-+=\[\]\\;'/`~]", password):
            raise ValueError("Password must contain at least one special character")
        return password


class VerifyEmailRequest(BaseModel):
    """
    Schema for email verification request.

    Attributes:
        token: Email verification token
    """

    token: str = Field(
        ...,
        min_length=1,
        description="Email verification token",
    )


class MessageResponse(BaseModel):
    """
    Simple message response schema.

    Used for endpoints that return only a status message.

    Attributes:
        message: Response message
    """

    message: str = Field(
        ...,
        description="Response message",
    )


class GoogleAuthRequest(BaseModel):
    """
    Schema for Google OAuth authentication request.

    Attributes:
        id_token: The Google ID token obtained from Google Sign-In
    """

    id_token: str = Field(
        ...,
        min_length=1,
        description="Google ID token from Google Sign-In",
        examples=["eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9..."],
    )


class GoogleUserInfo(BaseModel):
    """
    Schema for Google user profile information extracted from ID token.

    Attributes:
        sub: Google user ID (unique identifier)
        email: User's email address
        email_verified: Whether Google has verified the email
        name: User's full name
        given_name: User's first name
        family_name: User's last name
        picture: URL to user's profile picture
    """

    sub: str = Field(
        ...,
        description="Google user ID",
    )
    email: EmailStr = Field(
        ...,
        description="User's email address",
    )
    email_verified: bool = Field(
        default=False,
        description="Whether Google has verified the email",
    )
    name: str | None = Field(
        default=None,
        description="User's full name",
    )
    given_name: str | None = Field(
        default=None,
        description="User's first name",
    )
    family_name: str | None = Field(
        default=None,
        description="User's last name",
    )
    picture: str | None = Field(
        default=None,
        description="URL to user's profile picture",
    )
