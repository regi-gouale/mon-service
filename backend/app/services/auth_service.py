"""
Authentication Service.

Business logic for user authentication, registration,
and token management operations.
"""

import secrets
from datetime import UTC, datetime, timedelta
from typing import cast

import jwt
from sqlalchemy import CursorResult, delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.exceptions import (
    AlreadyExistsError,
    NotFoundError,
    UnauthorizedError,
)
from app.core.logging import get_logger
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    get_password_hash,
    verify_password,
)
from app.models.refresh_token import RefreshToken
from app.models.user import UserRole
from app.repositories.user_repository import UserRepository
from app.schemas.auth import (
    AuthResponse,
    RegisterRequest,
    UserResponse,
)

logger = get_logger(__name__)


class AuthService:
    """
    Authentication service for handling user auth operations.

    Provides business logic for:
    - User registration
    - Login/logout
    - Token management (access/refresh)
    - Password reset flow

    Attributes:
        session: Async database session for data operations.
        user_repository: Repository for user data access.
    """

    def __init__(self, session: AsyncSession) -> None:
        """
        Initialize the auth service.

        Args:
            session: Async SQLAlchemy session for database operations.
        """
        self.session = session
        self.user_repository = UserRepository(session)

    async def register(
        self,
        data: RegisterRequest,
        organization_id: str | None = None,
    ) -> AuthResponse:
        """
        Register a new user.

        Creates a new user account with hashed password,
        generates authentication tokens, and stores refresh token.

        Args:
            data: Registration data (email, password, first_name, last_name).
            organization_id: Optional organization to associate user with.

        Returns:
            AuthResponse: Access token, refresh token, and user data.

        Raises:
            AlreadyExistsError: If email is already registered.
        """
        logger.info(
            "Processing registration request",
            extra={"email": data.email},
        )

        # Check if user already exists
        existing_user = await self.user_repository.get_by_email(data.email)
        if existing_user:
            logger.warning(
                "Registration failed: email already exists",
                extra={"email": data.email},
            )
            raise AlreadyExistsError(
                resource="User",
                field="email",
                value=data.email,
            )

        # Hash the password
        password_hash = get_password_hash(data.password)

        # Create the user
        user = await self.user_repository.create(
            email=data.email,
            password_hash=password_hash,
            first_name=data.first_name,
            last_name=data.last_name,
            organization_id=organization_id,
            role=UserRole.MEMBER,
            email_verified=False,
        )

        # Generate tokens
        access_token = create_access_token(subject=user.id)
        refresh_token_str = create_refresh_token(subject=user.id)

        # Store refresh token in database
        await self._store_refresh_token(user.id, refresh_token_str)

        # Commit the transaction
        await self.session.commit()

        logger.info(
            "User registered successfully",
            extra={"user_id": user.id, "email": user.email},
        )

        return AuthResponse(
            access_token=access_token,
            refresh_token=refresh_token_str,
            token_type="bearer",
            user=UserResponse(
                id=user.id,
                email=user.email,
                first_name=user.first_name,
                last_name=user.last_name,
                role=user.role.value if isinstance(user.role, UserRole) else user.role,
                email_verified=user.email_verified,
                avatar_url=user.avatar_url,
                created_at=user.created_at,
            ),
        )

    async def login(self, email: str, password: str) -> AuthResponse:
        """
        Authenticate a user with email and password.

        Validates credentials, updates last login timestamp,
        and generates new authentication tokens.

        Args:
            email: User's email address.
            password: User's plain text password.

        Returns:
            AuthResponse: Access token, refresh token, and user data.

        Raises:
            UnauthorizedError: If credentials are invalid.
        """
        logger.info(
            "Processing login request",
            extra={"email": email},
        )

        # Find user by email
        user = await self.user_repository.get_by_email(email)
        if not user:
            logger.warning(
                "Login failed: user not found",
                extra={"email": email},
            )
            raise UnauthorizedError(message="Invalid email or password")

        # Check if account is active
        if not user.is_active:
            logger.warning(
                "Login failed: account inactive",
                extra={"user_id": user.id, "email": email},
            )
            raise UnauthorizedError(message="Account is deactivated")

        # Verify password
        if not user.password_hash or not verify_password(password, user.password_hash):
            logger.warning(
                "Login failed: invalid password",
                extra={"user_id": user.id, "email": email},
            )
            raise UnauthorizedError(message="Invalid email or password")

        # Update last login timestamp
        await self.user_repository.update_last_login(user.id)

        # Generate tokens
        access_token = create_access_token(subject=user.id)
        refresh_token_str = create_refresh_token(subject=user.id)

        # Store refresh token
        await self._store_refresh_token(user.id, refresh_token_str)

        # Commit the transaction
        await self.session.commit()

        logger.info(
            "User logged in successfully",
            extra={"user_id": user.id, "email": user.email},
        )

        return AuthResponse(
            access_token=access_token,
            refresh_token=refresh_token_str,
            token_type="bearer",
            user=UserResponse(
                id=user.id,
                email=user.email,
                first_name=user.first_name,
                last_name=user.last_name,
                role=user.role.value if isinstance(user.role, UserRole) else user.role,
                email_verified=user.email_verified,
                avatar_url=user.avatar_url,
                created_at=user.created_at,
            ),
        )

    async def refresh_token(self, refresh_token_str: str) -> AuthResponse:
        """
        Refresh access token using a valid refresh token.

        Validates the refresh token, revokes it, and issues new tokens.
        Implements token rotation for security.

        Args:
            refresh_token_str: The refresh token to exchange.

        Returns:
            AuthResponse: New access token, refresh token, and user data.

        Raises:
            UnauthorizedError: If refresh token is invalid or expired.
        """
        logger.debug("Processing token refresh request")

        # Decode and validate the refresh token JWT
        try:
            payload = decode_token(refresh_token_str)
        except jwt.ExpiredSignatureError:
            logger.warning("Token refresh failed: token expired")
            raise UnauthorizedError(message="Refresh token has expired")
        except jwt.InvalidTokenError as e:
            logger.warning(
                "Token refresh failed: invalid token",
                extra={"error": str(e)},
            )
            raise UnauthorizedError(message="Invalid refresh token")

        # Verify token type
        if payload.get("type") != "refresh":
            logger.warning("Token refresh failed: wrong token type")
            raise UnauthorizedError(message="Invalid token type")

        user_id = payload.get("sub")
        if not user_id:
            logger.warning("Token refresh failed: no subject in token")
            raise UnauthorizedError(message="Invalid refresh token")

        # Find the stored refresh token
        query = select(RefreshToken).where(
            RefreshToken.token == refresh_token_str,
            RefreshToken.user_id == user_id,
            RefreshToken.is_revoked.is_(False),
        )
        result = await self.session.execute(query)
        stored_token = result.scalar_one_or_none()

        if not stored_token:
            logger.warning(
                "Token refresh failed: token not found or revoked",
                extra={"user_id": user_id},
            )
            raise UnauthorizedError(message="Refresh token not found or revoked")

        # Check if token is expired in database
        now = datetime.now(UTC)
        # Handle timezone-naive datetimes (e.g., from SQLite)
        token_expires = stored_token.expires_at
        if token_expires.tzinfo is None:
            token_expires = token_expires.replace(tzinfo=UTC)

        if token_expires < now:
            logger.warning(
                "Token refresh failed: token expired in database",
                extra={"user_id": user_id},
            )
            raise UnauthorizedError(message="Refresh token has expired")

        # Get the user
        user = await self.user_repository.get_by_id(user_id)
        if not user or not user.is_active:
            logger.warning(
                "Token refresh failed: user not found or inactive",
                extra={"user_id": user_id},
            )
            raise UnauthorizedError(message="User not found or inactive")

        # Revoke the old refresh token (rotation)
        stored_token.is_revoked = True
        await self.session.flush()

        # Generate new tokens
        new_access_token = create_access_token(subject=user.id)
        new_refresh_token = create_refresh_token(subject=user.id)

        # Store new refresh token
        await self._store_refresh_token(user.id, new_refresh_token)

        # Commit the transaction
        await self.session.commit()

        logger.info(
            "Token refreshed successfully",
            extra={"user_id": user.id},
        )

        return AuthResponse(
            access_token=new_access_token,
            refresh_token=new_refresh_token,
            token_type="bearer",
            user=UserResponse(
                id=user.id,
                email=user.email,
                first_name=user.first_name,
                last_name=user.last_name,
                role=user.role.value if isinstance(user.role, UserRole) else user.role,
                email_verified=user.email_verified,
                avatar_url=user.avatar_url,
                created_at=user.created_at,
            ),
        )

    async def logout(
        self,
        user_id: str,
        refresh_token_str: str | None = None,
        revoke_all: bool = False,
    ) -> None:
        """
        Logout a user by revoking their refresh tokens.

        Can revoke a specific token or all tokens for the user.

        Args:
            user_id: The user's ID.
            refresh_token_str: Specific refresh token to revoke (optional).
            revoke_all: If True, revoke all user's refresh tokens.

        Raises:
            NotFoundError: If specified token not found.
        """
        logger.info(
            "Processing logout request",
            extra={"user_id": user_id, "revoke_all": revoke_all},
        )

        if revoke_all:
            # Revoke all refresh tokens for the user
            stmt = (
                update(RefreshToken)
                .where(
                    RefreshToken.user_id == user_id,
                    RefreshToken.is_revoked.is_(False),
                )
                .values(is_revoked=True)
            )
            await self.session.execute(stmt)
            logger.info(
                "All refresh tokens revoked",
                extra={"user_id": user_id},
            )
        elif refresh_token_str:
            # Revoke specific refresh token
            query = select(RefreshToken).where(
                RefreshToken.token == refresh_token_str,
                RefreshToken.user_id == user_id,
            )
            result = await self.session.execute(query)
            token = result.scalar_one_or_none()

            if not token:
                logger.warning(
                    "Logout failed: token not found",
                    extra={"user_id": user_id},
                )
                raise NotFoundError(resource="RefreshToken", resource_id="provided")

            token.is_revoked = True
            logger.info(
                "Refresh token revoked",
                extra={"user_id": user_id, "token_id": token.id},
            )
        else:
            # No specific action, just log
            logger.info(
                "Logout without token revocation",
                extra={"user_id": user_id},
            )

        await self.session.commit()

    async def forgot_password(self, email: str) -> str:
        """
        Initiate password reset flow.

        Generates a password reset token for the user.
        The token should be sent via email (email sending is handled separately).

        Args:
            email: User's email address.

        Returns:
            str: The password reset token (to be sent via email).

        Raises:
            NotFoundError: If user with email not found.

        Note:
            For security, in production the error should not reveal
            whether the email exists. This is handled at the API layer.
        """
        logger.info(
            "Processing forgot password request",
            extra={"email": email},
        )

        user = await self.user_repository.get_by_email(email)
        if not user:
            logger.warning(
                "Forgot password: user not found",
                extra={"email": email},
            )
            raise NotFoundError(resource="User", resource_id=email)

        # Generate a secure reset token
        reset_token = secrets.token_urlsafe(32)

        # Calculate expiration (1 hour from now)
        expires_at = datetime.now(UTC) + timedelta(hours=1)

        # Store reset token in a dedicated table or user field
        # For now, we'll use a combination stored approach
        # In production, this should be stored in a PasswordResetToken table
        # For this implementation, we'll encode it in the token itself
        reset_payload = {
            "sub": user.id,
            "email": user.email,
            "type": "password_reset",
            "token": reset_token,
            "exp": expires_at,
            "iat": datetime.now(UTC),
        }

        # Create a JWT for the reset token
        encoded_reset_token: str = jwt.encode(
            reset_payload,
            settings.secret_key,
            algorithm=settings.jwt_algorithm,
        )

        logger.info(
            "Password reset token generated",
            extra={"user_id": user.id, "email": email},
        )

        return encoded_reset_token

    async def reset_password(self, token: str, new_password: str) -> None:
        """
        Reset user's password using a valid reset token.

        Validates the reset token and updates the user's password.
        Also revokes all existing refresh tokens for security.

        Args:
            token: The password reset token.
            new_password: The new password (plain text, will be hashed).

        Raises:
            UnauthorizedError: If token is invalid or expired.
            BusinessRuleError: If password doesn't meet requirements.
        """
        logger.info("Processing password reset request")

        # Decode and validate the reset token
        try:
            payload = decode_token(token)
        except jwt.ExpiredSignatureError:
            logger.warning("Password reset failed: token expired")
            raise UnauthorizedError(message="Reset token has expired")
        except jwt.InvalidTokenError as e:
            logger.warning(
                "Password reset failed: invalid token",
                extra={"error": str(e)},
            )
            raise UnauthorizedError(message="Invalid reset token")

        # Verify token type
        if payload.get("type") != "password_reset":
            logger.warning("Password reset failed: wrong token type")
            raise UnauthorizedError(message="Invalid token type")

        user_id = payload.get("sub")
        if not user_id:
            logger.warning("Password reset failed: no subject in token")
            raise UnauthorizedError(message="Invalid reset token")

        # Get the user
        user = await self.user_repository.get_by_id(user_id)
        if not user:
            logger.warning(
                "Password reset failed: user not found",
                extra={"user_id": user_id},
            )
            raise UnauthorizedError(message="User not found")

        # Hash the new password
        new_password_hash = get_password_hash(new_password)

        # Update the password
        await self.user_repository.update(
            user_id=user.id,
            password_hash=new_password_hash,
        )

        # Revoke all refresh tokens for security
        stmt = (
            update(RefreshToken)
            .where(
                RefreshToken.user_id == user.id,
                RefreshToken.is_revoked.is_(False),
            )
            .values(is_revoked=True)
        )
        await self.session.execute(stmt)

        await self.session.commit()

        logger.info(
            "Password reset successfully",
            extra={"user_id": user.id},
        )

    async def verify_email(self, token: str) -> None:
        """
        Verify user's email address using a verification token.

        Args:
            token: The email verification token.

        Raises:
            UnauthorizedError: If token is invalid or expired.
        """
        logger.info("Processing email verification request")

        # Decode and validate the verification token
        try:
            payload = decode_token(token)
        except jwt.ExpiredSignatureError:
            logger.warning("Email verification failed: token expired")
            raise UnauthorizedError(message="Verification token has expired")
        except jwt.InvalidTokenError as e:
            logger.warning(
                "Email verification failed: invalid token",
                extra={"error": str(e)},
            )
            raise UnauthorizedError(message="Invalid verification token")

        # Verify token type
        if payload.get("type") != "email_verification":
            logger.warning("Email verification failed: wrong token type")
            raise UnauthorizedError(message="Invalid token type")

        user_id = payload.get("sub")
        if not user_id:
            logger.warning("Email verification failed: no subject in token")
            raise UnauthorizedError(message="Invalid verification token")

        # Verify the email
        await self.user_repository.verify_email(user_id)
        await self.session.commit()

        logger.info(
            "Email verified successfully",
            extra={"user_id": user_id},
        )

    async def create_email_verification_token(self, user_id: str) -> str:
        """
        Create an email verification token for a user.

        Args:
            user_id: The user's ID.

        Returns:
            str: The email verification token.

        Raises:
            NotFoundError: If user not found.
        """
        user = await self.user_repository.get_by_id(user_id)
        if not user:
            raise NotFoundError(resource="User", resource_id=user_id)

        # Generate verification token (expires in 24 hours)
        verification_payload = {
            "sub": user.id,
            "email": user.email,
            "type": "email_verification",
            "exp": datetime.now(UTC) + timedelta(hours=24),
            "iat": datetime.now(UTC),
        }

        encoded_token: str = jwt.encode(
            verification_payload,
            settings.secret_key,
            algorithm=settings.jwt_algorithm,
        )

        logger.info(
            "Email verification token created",
            extra={"user_id": user_id},
        )

        return encoded_token

    async def _store_refresh_token(self, user_id: str, token: str) -> RefreshToken:
        """
        Store a refresh token in the database.

        Args:
            user_id: The user's ID.
            token: The refresh token string.

        Returns:
            RefreshToken: The created refresh token record.
        """
        expires_at = datetime.now(UTC) + timedelta(
            days=settings.refresh_token_expire_days
        )

        refresh_token = RefreshToken(
            user_id=user_id,
            token=token,
            expires_at=expires_at,
            is_revoked=False,
        )

        self.session.add(refresh_token)
        await self.session.flush()

        return refresh_token

    async def cleanup_expired_tokens(self, user_id: str | None = None) -> int:
        """
        Clean up expired refresh tokens.

        Can clean up for a specific user or all users.

        Args:
            user_id: Optional user ID to clean up tokens for.

        Returns:
            int: Number of tokens deleted.
        """
        logger.info(
            "Cleaning up expired tokens",
            extra={"user_id": user_id},
        )

        now = datetime.now(UTC)

        if user_id:
            stmt = delete(RefreshToken).where(
                RefreshToken.user_id == user_id,
                RefreshToken.expires_at < now,
            )
        else:
            stmt = delete(RefreshToken).where(RefreshToken.expires_at < now)

        result = await self.session.execute(stmt)
        await self.session.commit()

        # Cast to CursorResult to access rowcount (available for DML statements)
        cursor_result = cast(CursorResult[tuple[()]], result)
        deleted_count: int = (
            cursor_result.rowcount if cursor_result.rowcount >= 0 else 0
        )

        logger.info(
            "Expired tokens cleaned up",
            extra={"deleted_count": deleted_count, "user_id": user_id},
        )

        return deleted_count
