"""Core module - configuration, security, database, exceptions."""

from app.core.config import Settings, get_settings, settings
from app.core.database import Base, async_session_maker, get_async_session
from app.core.exceptions import (
    AlreadyExistsError,
    AppException,
    BusinessRuleError,
    ForbiddenError,
    NotFoundError,
    UnauthorizedError,
    ValidationError,
)
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    get_password_hash,
    verify_password,
)

__all__ = [
    # Config
    "Settings",
    "get_settings",
    "settings",
    # Database
    "Base",
    "async_session_maker",
    "get_async_session",
    # Exceptions
    "AppException",
    "NotFoundError",
    "AlreadyExistsError",
    "UnauthorizedError",
    "ForbiddenError",
    "ValidationError",
    "BusinessRuleError",
    # Security
    "verify_password",
    "get_password_hash",
    "create_access_token",
    "create_refresh_token",
    "decode_token",
]
