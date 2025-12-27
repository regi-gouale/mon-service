"""
User Profile Routes.

API endpoints for user profile management including:
- Get current user profile
- Update profile
- Change password
- Delete account (soft delete, GDPR)
- Export user data (GDPR)
"""

from datetime import UTC, datetime
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, UploadFile, status

from app.api.v1.dependencies import DbSession, get_current_active_user
from app.core.logging import get_logger
from app.core.security import get_password_hash, verify_password
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.user import (
    ChangePasswordRequest,
    DataExportResponse,
    DeleteAccountRequest,
    UpdateProfileRequest,
    UserProfileResponse,
)

logger = get_logger(__name__)

router = APIRouter(prefix="/users", tags=["users"])


# Type alias for current user dependency
CurrentUser = User


@router.get(
    "/me",
    response_model=UserProfileResponse,
    summary="Get current user profile",
    description="Returns the complete profile of the authenticated user.",
)
async def get_current_user_profile(
    current_user: CurrentUser = Depends(get_current_active_user),
) -> UserProfileResponse:
    """
    Get the current user's profile.

    Returns complete profile information including:
    - Personal information (name, email, phone)
    - Account status (verified, active)
    - Notification preferences
    - Timestamps (created, last login)
    """
    return UserProfileResponse(
        id=current_user.id,
        email=current_user.email,
        first_name=current_user.first_name,
        last_name=current_user.last_name,
        phone=current_user.phone,
        avatar_url=current_user.avatar_url,
        role=current_user.role.value,
        email_verified=current_user.email_verified,
        is_active=current_user.is_active,
        organization_id=current_user.organization_id,
        notification_preferences=current_user.notification_preferences,
        last_login_at=current_user.last_login_at,
        created_at=current_user.created_at,
    )


@router.patch(
    "/me",
    response_model=UserProfileResponse,
    summary="Update current user profile",
    description="Update the authenticated user's profile information.",
)
async def update_current_user_profile(
    data: UpdateProfileRequest,
    session: DbSession,
    current_user: CurrentUser = Depends(get_current_active_user),
) -> UserProfileResponse:
    """
    Update the current user's profile.

    Only provided fields will be updated.
    Email cannot be changed through this endpoint.
    """
    user_repo = UserRepository(session)

    # Build update data from provided fields
    update_data: dict[str, Any] = {}

    if data.first_name is not None:
        update_data["first_name"] = data.first_name.strip()

    if data.last_name is not None:
        update_data["last_name"] = data.last_name.strip()

    if data.phone is not None:
        update_data["phone"] = data.phone.strip() if data.phone else None

    if data.notification_preferences is not None:
        update_data["notification_preferences"] = data.notification_preferences

    if update_data:
        update_data["updated_at"] = datetime.now(UTC)
        updated_user = await user_repo.update(current_user.id, **update_data)
        if not updated_user:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update profile",
            )
        current_user = updated_user

    logger.info(f"User profile updated: {current_user.id}")

    return UserProfileResponse(
        id=current_user.id,
        email=current_user.email,
        first_name=current_user.first_name,
        last_name=current_user.last_name,
        phone=current_user.phone,
        avatar_url=current_user.avatar_url,
        role=current_user.role.value,
        email_verified=current_user.email_verified,
        is_active=current_user.is_active,
        organization_id=current_user.organization_id,
        notification_preferences=current_user.notification_preferences,
        last_login_at=current_user.last_login_at,
        created_at=current_user.created_at,
    )


@router.post(
    "/me/change-password",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Change password",
    description="Change the current user's password.",
)
async def change_password(
    data: ChangePasswordRequest,
    session: DbSession,
    current_user: CurrentUser = Depends(get_current_active_user),
) -> None:
    """
    Change the current user's password.

    Requires the current password for verification.
    New password must meet security requirements.
    """
    # Verify current password
    if not current_user.password_hash:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot change password for OAuth accounts",
        )

    if not verify_password(data.current_password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Current password is incorrect",
        )

    # Update password
    user_repo = UserRepository(session)
    new_hash = get_password_hash(data.new_password)
    await user_repo.update(
        current_user.id,
        password_hash=new_hash,
        updated_at=datetime.now(UTC),
    )

    logger.info(f"Password changed for user: {current_user.id}")


@router.delete(
    "/me",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete account",
    description="Soft delete the current user's account (GDPR compliant).",
)
async def delete_account(
    data: DeleteAccountRequest,
    session: DbSession,
    current_user: CurrentUser = Depends(get_current_active_user),
) -> None:
    """
    Delete the current user's account.

    This performs a soft delete to comply with GDPR requirements:
    - Account is marked as deleted and deactivated
    - User data is retained for the required period (3 years)
    - User can no longer log in

    Requires password confirmation and explicit consent.
    """
    if not data.confirm:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Deletion must be explicitly confirmed",
        )

    # Verify password
    if current_user.password_hash and not verify_password(
        data.password, current_user.password_hash
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Password is incorrect",
        )

    # Soft delete
    user_repo = UserRepository(session)
    await user_repo.update(
        current_user.id,
        is_active=False,
        deleted_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )

    logger.info(f"Account soft deleted: {current_user.id}")


@router.get(
    "/me/data-export",
    response_model=DataExportResponse,
    summary="Export user data",
    description="Export all user data for GDPR compliance.",
)
async def export_user_data(
    session: DbSession,  # noqa: ARG001
    current_user: CurrentUser = Depends(get_current_active_user),
) -> DataExportResponse:
    """
    Export all user data for GDPR compliance.

    Returns a complete export of:
    - User profile information
    - Availability records
    - Planning assignments
    - Notifications

    This endpoint supports the GDPR right to data portability.
    """
    # Build user profile data
    user_data = {
        "id": current_user.id,
        "email": current_user.email,
        "firstName": current_user.first_name,
        "lastName": current_user.last_name,
        "phone": current_user.phone,
        "avatarUrl": current_user.avatar_url,
        "role": current_user.role.value,
        "emailVerified": current_user.email_verified,
        "organizationId": current_user.organization_id,
        "notificationPreferences": current_user.notification_preferences,
        "createdAt": current_user.created_at.isoformat()
        if current_user.created_at
        else None,
        "lastLoginAt": current_user.last_login_at.isoformat()
        if current_user.last_login_at
        else None,
    }

    # TODO: Add availability records when Availability model is implemented
    availabilities: list[dict[str, Any]] = []

    # TODO: Add assignments when PlanningAssignment model is implemented
    assignments: list[dict[str, Any]] = []

    # TODO: Add notifications when Notification model is implemented
    notifications: list[dict[str, Any]] = []

    logger.info(f"Data export requested by user: {current_user.id}")

    return DataExportResponse(
        user=user_data,
        availabilities=availabilities,
        assignments=assignments,
        notifications=notifications,
        exported_at=datetime.now(UTC),
    )


@router.post(
    "/me/avatar",
    response_model=UserProfileResponse,
    summary="Upload avatar",
    description="Upload a new avatar image for the current user.",
)
async def upload_avatar(
    file: UploadFile,
    session: DbSession,  # noqa: ARG001
    current_user: CurrentUser = Depends(get_current_active_user),
) -> UserProfileResponse:
    """
    Upload a new avatar image.

    Supported formats: JPEG, PNG, WebP
    Maximum size: 5MB

    The image will be stored in S3/MinIO and the URL updated in the user profile.
    """
    # Validate file type
    allowed_types = ["image/jpeg", "image/png", "image/webp"]
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file type. Allowed: {', '.join(allowed_types)}",
        )

    # Validate file size (5MB max)
    max_size = 5 * 1024 * 1024  # 5MB
    content = await file.read()
    if len(content) > max_size:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File too large. Maximum size is 5MB.",
        )

    # TODO: Implement S3/MinIO upload
    # For now, we'll just log and return a placeholder
    logger.info(
        f"Avatar upload requested by user: {current_user.id}, size: {len(content)} bytes"
    )

    # Placeholder: In production, upload to S3 and get URL
    # avatar_url = await s3_service.upload_avatar(current_user.id, content, file.content_type)

    # For now, return current profile without changes
    # TODO: Update this when S3 service is implemented

    return UserProfileResponse(
        id=current_user.id,
        email=current_user.email,
        first_name=current_user.first_name,
        last_name=current_user.last_name,
        phone=current_user.phone,
        avatar_url=current_user.avatar_url,
        role=current_user.role.value,
        email_verified=current_user.email_verified,
        is_active=current_user.is_active,
        organization_id=current_user.organization_id,
        notification_preferences=current_user.notification_preferences,
        last_login_at=current_user.last_login_at,
        created_at=current_user.created_at,
    )
