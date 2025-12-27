"""
User Repository.

Data access layer for User model operations.
Provides async CRUD operations with proper error handling.
"""

from datetime import UTC, datetime
from typing import Any

from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AlreadyExistsError, NotFoundError
from app.models.user import User, UserRole


class UserRepository:
    """
    Repository for User data access operations.

    Provides async CRUD operations for User model with proper
    error handling and soft delete support.

    Attributes:
        session: The async database session.
    """

    def __init__(self, session: AsyncSession) -> None:
        """
        Initialize the repository with a database session.

        Args:
            session: Async SQLAlchemy session for database operations.
        """
        self.session = session

    async def create(
        self,
        *,
        email: str,
        password_hash: str | None = None,
        first_name: str,
        last_name: str,
        organization_id: str | None = None,
        role: UserRole = UserRole.MEMBER,
        phone: str | None = None,
        avatar_url: str | None = None,
        email_verified: bool = False,
        is_active: bool = True,
        notification_preferences: dict[str, Any] | None = None,
    ) -> User:
        """
        Create a new user.

        Args:
            email: User's email address (must be unique).
            password_hash: Hashed password (None for OAuth users).
            first_name: User's first name.
            last_name: User's last name.
            organization_id: Optional organization ID.
            role: User role (default: MEMBER).
            phone: Optional phone number.
            avatar_url: Optional avatar URL.
            email_verified: Whether email is verified (default: False).
            is_active: Whether account is active (default: True).
            notification_preferences: Optional notification settings.

        Returns:
            User: The created user instance.

        Raises:
            AlreadyExistsError: If a user with the email already exists.
        """
        user = User(
            email=email.lower().strip(),
            password_hash=password_hash,
            first_name=first_name,
            last_name=last_name,
            organization_id=organization_id,
            role=role,
            phone=phone,
            avatar_url=avatar_url,
            email_verified=email_verified,
            is_active=is_active,
            notification_preferences=notification_preferences or {},
        )

        try:
            self.session.add(user)
            await self.session.flush()
            await self.session.refresh(user)
            return user
        except IntegrityError as e:
            await self.session.rollback()
            if "unique" in str(e.orig).lower() or "duplicate" in str(e.orig).lower():
                raise AlreadyExistsError(
                    resource="User",
                    field="email",
                    value=email,
                ) from e
            raise

    async def get_by_id(
        self,
        user_id: str,
        *,
        include_deleted: bool = False,
    ) -> User | None:
        """
        Retrieve a user by their ID.

        Args:
            user_id: The user's unique identifier.
            include_deleted: Whether to include soft-deleted users.

        Returns:
            User | None: The user if found, None otherwise.
        """
        query = select(User).where(User.id == user_id)

        if not include_deleted:
            query = query.where(User.deleted_at.is_(None))

        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_by_id_or_raise(
        self,
        user_id: str,
        *,
        include_deleted: bool = False,
    ) -> User:
        """
        Retrieve a user by their ID or raise NotFoundError.

        Args:
            user_id: The user's unique identifier.
            include_deleted: Whether to include soft-deleted users.

        Returns:
            User: The user if found.

        Raises:
            NotFoundError: If the user is not found.
        """
        user = await self.get_by_id(user_id, include_deleted=include_deleted)
        if user is None:
            raise NotFoundError(resource="User", resource_id=user_id)
        return user

    async def get_by_email(
        self,
        email: str,
        *,
        include_deleted: bool = False,
    ) -> User | None:
        """
        Retrieve a user by their email address.

        Args:
            email: The user's email address.
            include_deleted: Whether to include soft-deleted users.

        Returns:
            User | None: The user if found, None otherwise.
        """
        query = select(User).where(User.email == email.lower().strip())

        if not include_deleted:
            query = query.where(User.deleted_at.is_(None))

        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_by_email_or_raise(
        self,
        email: str,
        *,
        include_deleted: bool = False,
    ) -> User:
        """
        Retrieve a user by their email or raise NotFoundError.

        Args:
            email: The user's email address.
            include_deleted: Whether to include soft-deleted users.

        Returns:
            User: The user if found.

        Raises:
            NotFoundError: If the user is not found.
        """
        user = await self.get_by_email(email, include_deleted=include_deleted)
        if user is None:
            raise NotFoundError(resource="User", resource_id=email)
        return user

    async def update(
        self,
        user_id: str,
        *,
        email: str | None = None,
        password_hash: str | None = None,
        first_name: str | None = None,
        last_name: str | None = None,
        phone: str | None = None,
        avatar_url: str | None = None,
        role: UserRole | None = None,
        email_verified: bool | None = None,
        is_active: bool | None = None,
        organization_id: str | None = None,
        notification_preferences: dict[str, Any] | None = None,
        last_login_at: datetime | None = None,
    ) -> User:
        """
        Update a user's information.

        Only provided fields (non-None) will be updated.

        Args:
            user_id: The user's unique identifier.
            email: New email address.
            password_hash: New hashed password.
            first_name: New first name.
            last_name: New last name.
            phone: New phone number.
            avatar_url: New avatar URL.
            role: New role.
            email_verified: New email verified status.
            is_active: New active status.
            organization_id: New organization ID.
            notification_preferences: New notification preferences.
            last_login_at: Last login timestamp.

        Returns:
            User: The updated user instance.

        Raises:
            NotFoundError: If the user is not found.
            AlreadyExistsError: If the new email already exists.
        """
        # First, get the user to ensure it exists
        user = await self.get_by_id_or_raise(user_id)

        # Build update data from non-None values
        update_data: dict[str, Any] = {}

        if email is not None:
            update_data["email"] = email.lower().strip()
        if password_hash is not None:
            update_data["password_hash"] = password_hash
        if first_name is not None:
            update_data["first_name"] = first_name
        if last_name is not None:
            update_data["last_name"] = last_name
        if phone is not None:
            update_data["phone"] = phone
        if avatar_url is not None:
            update_data["avatar_url"] = avatar_url
        if role is not None:
            update_data["role"] = role
        if email_verified is not None:
            update_data["email_verified"] = email_verified
        if is_active is not None:
            update_data["is_active"] = is_active
        if organization_id is not None:
            update_data["organization_id"] = organization_id
        if notification_preferences is not None:
            update_data["notification_preferences"] = notification_preferences
        if last_login_at is not None:
            update_data["last_login_at"] = last_login_at

        if not update_data:
            return user

        try:
            stmt = (
                update(User)
                .where(User.id == user_id)
                .values(**update_data)
                .returning(User)
            )
            result = await self.session.execute(stmt)
            await self.session.flush()
            updated_user = result.scalar_one()
            await self.session.refresh(updated_user)
            return updated_user
        except IntegrityError as e:
            await self.session.rollback()
            if "unique" in str(e.orig).lower() or "duplicate" in str(e.orig).lower():
                raise AlreadyExistsError(
                    resource="User",
                    field="email",
                    value=email or "",
                ) from e
            raise

    async def delete(
        self,
        user_id: str,
        *,
        hard_delete: bool = False,
    ) -> bool:
        """
        Delete a user (soft delete by default).

        Soft delete marks the user as deleted without removing from database.
        Hard delete permanently removes the user from the database.

        Args:
            user_id: The user's unique identifier.
            hard_delete: If True, permanently delete. Default is soft delete.

        Returns:
            bool: True if the user was deleted.

        Raises:
            NotFoundError: If the user is not found.
        """
        user = await self.get_by_id_or_raise(user_id)

        if hard_delete:
            await self.session.delete(user)
        else:
            user.deleted_at = datetime.now(UTC)
            user.is_active = False

        await self.session.flush()
        return True

    async def restore(self, user_id: str) -> User:
        """
        Restore a soft-deleted user.

        Args:
            user_id: The user's unique identifier.

        Returns:
            User: The restored user instance.

        Raises:
            NotFoundError: If the user is not found.
        """
        user = await self.get_by_id_or_raise(user_id, include_deleted=True)

        if user.deleted_at is None:
            return user  # Already not deleted

        user.deleted_at = None
        user.is_active = True

        await self.session.flush()
        await self.session.refresh(user)
        return user

    async def list_by_organization(
        self,
        organization_id: str,
        *,
        include_deleted: bool = False,
        skip: int = 0,
        limit: int = 100,
    ) -> list[User]:
        """
        List all users in an organization.

        Args:
            organization_id: The organization's unique identifier.
            include_deleted: Whether to include soft-deleted users.
            skip: Number of records to skip (for pagination).
            limit: Maximum number of records to return.

        Returns:
            list[User]: List of users in the organization.
        """
        query = (
            select(User)
            .where(User.organization_id == organization_id)
            .offset(skip)
            .limit(limit)
            .order_by(User.created_at.desc())
        )

        if not include_deleted:
            query = query.where(User.deleted_at.is_(None))

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def count_by_organization(
        self,
        organization_id: str,
        *,
        include_deleted: bool = False,
    ) -> int:
        """
        Count users in an organization.

        Args:
            organization_id: The organization's unique identifier.
            include_deleted: Whether to include soft-deleted users.

        Returns:
            int: Number of users in the organization.
        """
        from sqlalchemy import func as sql_func

        query = (
            select(sql_func.count())
            .select_from(User)
            .where(User.organization_id == organization_id)
        )

        if not include_deleted:
            query = query.where(User.deleted_at.is_(None))

        result = await self.session.execute(query)
        return result.scalar_one()

    async def exists_by_email(self, email: str) -> bool:
        """
        Check if a user with the given email exists.

        Args:
            email: The email address to check.

        Returns:
            bool: True if a user with this email exists.
        """
        query = select(User.id).where(
            User.email == email.lower().strip(),
            User.deleted_at.is_(None),
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none() is not None

    async def update_last_login(self, user_id: str) -> User:
        """
        Update the user's last login timestamp.

        Args:
            user_id: The user's unique identifier.

        Returns:
            User: The updated user instance.

        Raises:
            NotFoundError: If the user is not found.
        """
        return await self.update(user_id, last_login_at=datetime.now(UTC))

    async def verify_email(self, user_id: str) -> User:
        """
        Mark a user's email as verified.

        Args:
            user_id: The user's unique identifier.

        Returns:
            User: The updated user instance.

        Raises:
            NotFoundError: If the user is not found.
        """
        return await self.update(user_id, email_verified=True)
