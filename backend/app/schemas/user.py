"""
User Profile Schemas.

Pydantic schemas for user profile management endpoints.
"""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, EmailStr, Field


class UserProfileResponse(BaseModel):
    """
    Schema for user profile response.

    Returns complete user profile information.
    """

    model_config = {"populate_by_name": True}

    id: str = Field(..., description="User's unique identifier")
    email: EmailStr = Field(..., description="User's email address")
    first_name: str = Field(..., alias="firstName", description="User's first name")
    last_name: str = Field(..., alias="lastName", description="User's last name")
    phone: str | None = Field(None, description="User's phone number")
    avatar_url: str | None = Field(
        None, alias="avatarUrl", description="URL to user's avatar"
    )
    role: str = Field(..., description="User's role in the organization")
    email_verified: bool = Field(
        ..., alias="emailVerified", description="Email verification status"
    )
    is_active: bool = Field(..., alias="isActive", description="Account active status")
    organization_id: str | None = Field(
        None, alias="organizationId", description="Organization ID"
    )
    notification_preferences: dict[str, Any] | None = Field(
        None, alias="notificationPreferences", description="Notification settings"
    )
    last_login_at: datetime | None = Field(
        None, alias="lastLoginAt", description="Last login timestamp"
    )
    created_at: datetime = Field(
        ..., alias="createdAt", description="Account creation timestamp"
    )


class UpdateProfileRequest(BaseModel):
    """
    Schema for updating user profile.

    All fields are optional - only provided fields will be updated.
    """

    model_config = {"populate_by_name": True}

    first_name: str | None = Field(
        None,
        alias="firstName",
        min_length=1,
        max_length=100,
        description="User's first name",
    )
    last_name: str | None = Field(
        None,
        alias="lastName",
        min_length=1,
        max_length=100,
        description="User's last name",
    )
    phone: str | None = Field(
        None,
        max_length=20,
        description="User's phone number",
    )
    notification_preferences: dict[str, Any] | None = Field(
        None,
        alias="notificationPreferences",
        description="Notification settings",
    )


class ChangePasswordRequest(BaseModel):
    """
    Schema for changing user password.
    """

    model_config = {"populate_by_name": True}

    current_password: str = Field(
        ...,
        alias="currentPassword",
        min_length=8,
        description="Current password",
    )
    new_password: str = Field(
        ...,
        alias="newPassword",
        min_length=8,
        max_length=128,
        description="New password",
    )


class DeleteAccountRequest(BaseModel):
    """
    Schema for account deletion confirmation.

    Requires password for security.
    """

    password: str = Field(
        ...,
        min_length=1,
        description="Current password for confirmation",
    )
    confirm: bool = Field(
        ...,
        description="Confirmation flag (must be True)",
    )


class DataExportResponse(BaseModel):
    """
    Schema for GDPR data export response.
    """

    model_config = {"populate_by_name": True}

    user: dict[str, Any] = Field(..., description="User profile data")
    availabilities: list[dict[str, Any]] = Field(
        default_factory=list, description="User's availability records"
    )
    assignments: list[dict[str, Any]] = Field(
        default_factory=list, description="User's planning assignments"
    )
    notifications: list[dict[str, Any]] = Field(
        default_factory=list, description="User's notifications"
    )
    exported_at: datetime = Field(
        ..., alias="exportedAt", description="Export timestamp"
    )
