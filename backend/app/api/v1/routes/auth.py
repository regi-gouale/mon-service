"""
Authentication API Routes.

REST endpoints for user authentication, registration,
and token management operations.
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.exceptions import (
    AlreadyExistsError,
    NotFoundError,
    UnauthorizedError,
)
from app.core.logging import get_logger
from app.schemas.auth import (
    AuthResponse,
    ForgotPasswordRequest,
    LoginRequest,
    MessageResponse,
    RefreshTokenRequest,
    RegisterRequest,
    ResetPasswordRequest,
    VerifyEmailRequest,
)
from app.services.auth_service import AuthService

logger = get_logger(__name__)

router = APIRouter(prefix="/auth", tags=["Authentication"])


# Type alias for database session dependency
DbSession = Annotated[AsyncSession, Depends(get_db)]


def get_auth_service(session: DbSession) -> AuthService:
    """
    Dependency to get an AuthService instance.

    Args:
        session: Database session from dependency injection.

    Returns:
        AuthService: Configured auth service instance.
    """
    return AuthService(session)


AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]


@router.post(
    "/register",
    response_model=AuthResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    description="""
    Create a new user account with email and password.

    The password must meet the following requirements:
    - At least 8 characters
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one digit
    - At least one special character

    Returns access and refresh tokens upon successful registration.
    """,
    responses={
        201: {
            "description": "User successfully registered",
            "model": AuthResponse,
        },
        409: {
            "description": "Email already registered",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "User with email 'user@example.com' already exists"
                    }
                }
            },
        },
        422: {
            "description": "Validation error",
            "content": {
                "application/json": {
                    "example": {
                        "detail": [
                            {
                                "loc": ["body", "password"],
                                "msg": "Password must contain at least one uppercase letter",
                                "type": "value_error",
                            }
                        ]
                    }
                }
            },
        },
    },
)
async def register(
    data: RegisterRequest,
    auth_service: AuthServiceDep,
) -> AuthResponse:
    """
    Register a new user account.

    Creates a new user with the provided credentials,
    generates authentication tokens, and returns them
    along with user data.
    """
    try:
        result = await auth_service.register(data)
        logger.info(
            "User registered via API",
            extra={"email": data.email},
        )
        return result
    except AlreadyExistsError as e:
        logger.warning(
            "Registration failed: email exists",
            extra={"email": data.email},
        )
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=e.message,
        ) from e


@router.post(
    "/login",
    response_model=AuthResponse,
    summary="Authenticate user",
    description="""
    Authenticate a user with email and password.

    Returns access and refresh tokens upon successful authentication.
    The access token should be included in the Authorization header
    for subsequent requests: `Authorization: Bearer <access_token>`
    """,
    responses={
        200: {
            "description": "Successfully authenticated",
            "model": AuthResponse,
        },
        401: {
            "description": "Invalid credentials",
            "content": {
                "application/json": {"example": {"detail": "Invalid email or password"}}
            },
        },
    },
)
async def login(
    data: LoginRequest,
    auth_service: AuthServiceDep,
) -> AuthResponse:
    """
    Authenticate a user with email and password.

    Validates credentials, generates new tokens,
    and updates the last login timestamp.
    """
    try:
        result = await auth_service.login(data.email, data.password)
        logger.info(
            "User logged in via API",
            extra={"email": data.email},
        )
        return result
    except UnauthorizedError as e:
        logger.warning(
            "Login failed",
            extra={"email": data.email, "reason": e.message},
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=e.message,
            headers={"WWW-Authenticate": "Bearer"},
        ) from e


@router.post(
    "/refresh",
    response_model=AuthResponse,
    summary="Refresh access token",
    description="""
    Exchange a valid refresh token for new access and refresh tokens.

    The old refresh token is revoked (token rotation) to prevent reuse.
    This endpoint should be called when the access token expires.
    """,
    responses={
        200: {
            "description": "Tokens refreshed successfully",
            "model": AuthResponse,
        },
        401: {
            "description": "Invalid or expired refresh token",
            "content": {
                "application/json": {"example": {"detail": "Refresh token has expired"}}
            },
        },
    },
)
async def refresh_token(
    data: RefreshTokenRequest,
    auth_service: AuthServiceDep,
) -> AuthResponse:
    """
    Refresh authentication tokens.

    Validates the refresh token, revokes it,
    and issues new access and refresh tokens.
    """
    try:
        result = await auth_service.refresh_token(data.refresh_token)
        logger.debug("Token refreshed via API")
        return result
    except UnauthorizedError as e:
        logger.warning(
            "Token refresh failed",
            extra={"reason": e.message},
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=e.message,
            headers={"WWW-Authenticate": "Bearer"},
        ) from e


@router.post(
    "/logout",
    response_model=MessageResponse,
    summary="Logout user",
    description="""
    Logout the current user by revoking their refresh token.

    If a refresh token is provided, only that token is revoked.
    The access token will remain valid until it expires.
    For immediate session termination, the client should discard
    the access token.
    """,
    responses={
        200: {
            "description": "Successfully logged out",
            "model": MessageResponse,
        },
        404: {
            "description": "Refresh token not found",
            "content": {
                "application/json": {"example": {"detail": "RefreshToken not found"}}
            },
        },
    },
)
async def logout(
    data: RefreshTokenRequest,
    auth_service: AuthServiceDep,
) -> MessageResponse:
    """
    Logout by revoking the refresh token.

    The provided refresh token is revoked and can no longer
    be used to obtain new access tokens.
    """
    try:
        # Decode token to get user_id
        from app.core.security import decode_token

        payload = decode_token(data.refresh_token)
        user_id = payload.get("sub")

        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token",
            )

        await auth_service.logout(user_id, data.refresh_token)
        logger.info(
            "User logged out via API",
            extra={"user_id": user_id},
        )
        return MessageResponse(message="Successfully logged out")
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.message,
        ) from e
    except Exception as e:
        logger.warning(
            "Logout failed",
            extra={"error": str(e)},
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        ) from e


@router.post(
    "/forgot-password",
    response_model=MessageResponse,
    summary="Request password reset",
    description="""
    Request a password reset email.

    If the email exists, a password reset token will be generated.
    For security reasons, this endpoint always returns success,
    even if the email doesn't exist in the system.

    The reset token should be sent via email (handled separately).
    """,
    responses={
        200: {
            "description": "Password reset email sent (if email exists)",
            "model": MessageResponse,
        },
    },
)
async def forgot_password(
    data: ForgotPasswordRequest,
    auth_service: AuthServiceDep,
) -> MessageResponse:
    """
    Initiate password reset flow.

    Generates a password reset token if the email exists.
    Always returns success to prevent email enumeration.
    """
    try:
        await auth_service.forgot_password(data.email)
        # In production, send this token via email
        # For now, just log that it was generated
        logger.info(
            "Password reset token generated",
            extra={"email": data.email, "token_generated": True},
        )
        # TODO: Integrate with email service to send reset link
        # await email_service.send_password_reset_email(data.email, reset_token)
    except NotFoundError:
        # Don't reveal whether email exists (security best practice)
        logger.info(
            "Password reset requested for unknown email",
            extra={"email": data.email},
        )

    # Always return success to prevent email enumeration
    return MessageResponse(
        message="If the email exists, a password reset link has been sent"
    )


@router.post(
    "/reset-password",
    response_model=MessageResponse,
    summary="Reset password with token",
    description="""
    Reset the user's password using a valid reset token.

    The token must be obtained from the forgot-password flow.
    After successful reset, all refresh tokens are revoked
    for security (forces re-login on all devices).

    The new password must meet the same requirements as registration.
    """,
    responses={
        200: {
            "description": "Password successfully reset",
            "model": MessageResponse,
        },
        401: {
            "description": "Invalid or expired reset token",
            "content": {
                "application/json": {"example": {"detail": "Reset token has expired"}}
            },
        },
        422: {
            "description": "Password validation error",
        },
    },
)
async def reset_password(
    data: ResetPasswordRequest,
    auth_service: AuthServiceDep,
) -> MessageResponse:
    """
    Reset password using a reset token.

    Validates the token, updates the password,
    and revokes all existing refresh tokens.
    """
    try:
        await auth_service.reset_password(data.token, data.password)
        logger.info("Password reset successfully via API")
        return MessageResponse(message="Password successfully reset")
    except UnauthorizedError as e:
        logger.warning(
            "Password reset failed",
            extra={"reason": e.message},
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=e.message,
        ) from e


@router.post(
    "/verify-email",
    response_model=MessageResponse,
    summary="Verify email address",
    description="""
    Verify the user's email address using a verification token.

    The token is sent to the user's email after registration.
    """,
    responses={
        200: {
            "description": "Email successfully verified",
            "model": MessageResponse,
        },
        401: {
            "description": "Invalid or expired verification token",
        },
    },
)
async def verify_email(
    data: VerifyEmailRequest,
    auth_service: AuthServiceDep,
) -> MessageResponse:
    """
    Verify user's email address.

    Validates the verification token and marks
    the user's email as verified.
    """
    try:
        await auth_service.verify_email(data.token)
        logger.info("Email verified successfully via API")
        return MessageResponse(message="Email successfully verified")
    except UnauthorizedError as e:
        logger.warning(
            "Email verification failed",
            extra={"reason": e.message},
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=e.message,
        ) from e
