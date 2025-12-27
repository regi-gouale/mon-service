"""
API v1 Dependencies.

This module contains FastAPI dependency injection functions
for authentication, database sessions, and other shared resources.

Usage:
    from app.api.v1.dependencies import get_current_user, get_current_active_user

    @router.get("/protected")
    async def protected_route(
        current_user: User = Depends(get_current_user)
    ):
        return {"user_id": current_user.id}
"""

from collections.abc import Callable, Coroutine
from typing import Annotated, Any

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.logging import get_logger
from app.core.security import decode_token
from app.models.user import User, UserRole
from app.repositories.user_repository import UserRepository

logger = get_logger(__name__)

# HTTP Bearer token security scheme
# auto_error=False allows us to handle missing tokens gracefully
security = HTTPBearer(auto_error=False)


# Type aliases for dependency injection
DbSession = Annotated[AsyncSession, Depends(get_db)]
OptionalCredentials = Annotated[HTTPAuthorizationCredentials | None, Depends(security)]


async def get_current_user(
    credentials: OptionalCredentials,
    session: DbSession,
) -> User:
    """
    Extract and validate the current user from the JWT token.

    This dependency:
    1. Extracts the Bearer token from the Authorization header
    2. Decodes and validates the JWT
    3. Loads the user from the database
    4. Returns the user object for use in route handlers

    Args:
        credentials: HTTP Bearer credentials from the Authorization header.
        session: Database session for user lookup.

    Returns:
        User: The authenticated user.

    Raises:
        HTTPException: 401 if token is missing, invalid, or expired.
        HTTPException: 401 if user not found in database.
    """
    # Check if credentials are provided
    if credentials is None:
        logger.warning("Authentication failed: no credentials provided")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials

    # Decode and validate the token
    try:
        payload = decode_token(token)
    except jwt.ExpiredSignatureError:
        logger.warning("Authentication failed: token expired")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError as e:
        logger.warning(
            "Authentication failed: invalid token",
            extra={"error": str(e)},
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Verify token type is access token
    token_type = payload.get("type")
    if token_type != "access":
        logger.warning(
            "Authentication failed: wrong token type",
            extra={"token_type": token_type},
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Extract user ID from token
    user_id = payload.get("sub")
    if not user_id:
        logger.warning("Authentication failed: no subject in token")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Load user from database
    user_repository = UserRepository(session)
    user = await user_repository.get_by_id(user_id)

    if not user:
        logger.warning(
            "Authentication failed: user not found",
            extra={"user_id": user_id},
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    logger.debug(
        "User authenticated successfully",
        extra={"user_id": user.id, "email": user.email},
    )

    return user


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    """
    Get the current user and verify they are active.

    This dependency builds on get_current_user and adds an additional
    check to ensure the user account is active (not deactivated).

    Args:
        current_user: The authenticated user from get_current_user.

    Returns:
        User: The authenticated and active user.

    Raises:
        HTTPException: 403 if user account is deactivated.
    """
    if not current_user.is_active:
        logger.warning(
            "Access denied: user account is deactivated",
            extra={"user_id": current_user.id},
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is deactivated",
        )

    return current_user


async def get_current_verified_user(
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> User:
    """
    Get the current user and verify their email is verified.

    This dependency builds on get_current_active_user and adds an additional
    check to ensure the user's email has been verified.

    Args:
        current_user: The authenticated and active user.

    Returns:
        User: The authenticated, active, and verified user.

    Raises:
        HTTPException: 403 if user email is not verified.
    """
    if not current_user.email_verified:
        logger.warning(
            "Access denied: email not verified",
            extra={"user_id": current_user.id},
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email verification required",
        )

    return current_user


def require_role(
    *allowed_roles: UserRole,
) -> Callable[
    [Annotated[User, Depends(get_current_active_user)]], Coroutine[Any, Any, User]
]:
    """
    Factory function to create a dependency that checks user roles.

    Creates a dependency that verifies the current user has one of
    the specified roles.

    Args:
        *allowed_roles: Variable number of UserRole values that are allowed.

    Returns:
        Callable: A FastAPI dependency function.

    Example:
        @router.get("/admin-only")
        async def admin_route(
            current_user: User = Depends(require_role(UserRole.ADMIN))
        ):
            return {"message": "Admin access granted"}

        @router.get("/managers")
        async def manager_route(
            current_user: User = Depends(require_role(UserRole.ADMIN, UserRole.MANAGER))
        ):
            return {"message": "Manager or admin access"}
    """

    async def role_checker(
        current_user: Annotated[User, Depends(get_current_active_user)],
    ) -> User:
        """Check if the current user has one of the allowed roles."""
        user_role = current_user.role
        if isinstance(user_role, str):
            user_role = UserRole(user_role)

        if user_role not in allowed_roles:
            logger.warning(
                "Access denied: insufficient role",
                extra={
                    "user_id": current_user.id,
                    "user_role": current_user.role,
                    "required_roles": [r.value for r in allowed_roles],
                },
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )

        return current_user

    return role_checker


async def get_optional_current_user(
    credentials: OptionalCredentials,
    session: DbSession,
) -> User | None:
    """
    Optionally extract the current user from the JWT token.

    Similar to get_current_user, but returns None instead of raising
    an exception if no token is provided or if the token is invalid.
    Useful for routes that behave differently for authenticated vs
    anonymous users.

    Args:
        credentials: HTTP Bearer credentials from the Authorization header.
        session: Database session for user lookup.

    Returns:
        User | None: The authenticated user, or None if not authenticated.
    """
    if credentials is None:
        return None

    token = credentials.credentials

    try:
        payload = decode_token(token)
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        return None

    if payload.get("type") != "access":
        return None

    user_id = payload.get("sub")
    if not user_id:
        return None

    user_repository = UserRepository(session)
    user = await user_repository.get_by_id(user_id)

    if user and user.is_active:
        return user

    return None


# Type aliases for cleaner route signatures
CurrentUser = Annotated[User, Depends(get_current_user)]
CurrentActiveUser = Annotated[User, Depends(get_current_active_user)]
CurrentVerifiedUser = Annotated[User, Depends(get_current_verified_user)]
OptionalUser = Annotated[User | None, Depends(get_optional_current_user)]

__all__ = [
    # Dependencies
    "get_current_user",
    "get_current_active_user",
    "get_current_verified_user",
    "get_optional_current_user",
    "require_role",
    # Type aliases
    "CurrentUser",
    "CurrentActiveUser",
    "CurrentVerifiedUser",
    "OptionalUser",
    "DbSession",
    # Security scheme
    "security",
]
