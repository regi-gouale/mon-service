"""Schemas module - Pydantic schemas for request/response validation."""

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
from app.schemas.availability import (
    AvailabilityCreate,
    AvailabilityDeadlineResponse,
    AvailabilityResponse,
    DepartmentAvailabilityResponse,
    MemberAvailabilityResponse,
    SetAvailabilitiesRequest,
)

__all__ = [
    # Auth schemas
    "AuthResponse",
    "ForgotPasswordRequest",
    "LoginRequest",
    "MessageResponse",
    "RefreshTokenRequest",
    "RegisterRequest",
    "ResetPasswordRequest",
    "TokenPayload",
    "UserResponse",
    "VerifyEmailRequest",
    # Availability schemas
    "AvailabilityCreate",
    "AvailabilityDeadlineResponse",
    "AvailabilityResponse",
    "DepartmentAvailabilityResponse",
    "MemberAvailabilityResponse",
    "SetAvailabilitiesRequest",
]
