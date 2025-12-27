"""
Member Repository.

Data access layer for Member model operations.
Provides async CRUD operations with proper error handling.
"""

from typing import Any

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.exceptions import AlreadyExistsError, NotFoundError
from app.models.member import Member, MemberRole, MemberStatus


class MemberRepository:
    """
    Repository for Member data access operations.

    Provides async CRUD operations for Member model with proper
    error handling and multi-tenancy support.

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
        organization_id: str,
        department_id: str,
        user_id: str,
        role: MemberRole = MemberRole.MEMBER,
        skills: list[str] | None = None,
        status: MemberStatus = MemberStatus.ACTIVE,
    ) -> Member:
        """
        Create a new membership.

        Args:
            organization_id: Organization this membership belongs to.
            department_id: Department the user is joining.
            user_id: User joining the department.
            role: Role within the department.
            skills: List of skills/competencies.
            status: Membership status.

        Returns:
            Member: The created membership instance.

        Raises:
            AlreadyExistsError: If the user is already a member of this department.
        """
        member = Member(
            organization_id=organization_id,
            department_id=department_id,
            user_id=user_id,
            role=role,
            skills=skills or [],
            status=status,
        )

        try:
            self.session.add(member)
            await self.session.flush()
            await self.session.refresh(member)
            return member
        except IntegrityError as e:
            await self.session.rollback()
            if "unique" in str(e.orig).lower() or "duplicate" in str(e.orig).lower():
                raise AlreadyExistsError(
                    resource="Member",
                    field="user_id",
                    value=f"{user_id} in department {department_id}",
                ) from e
            raise

    async def get_by_id(
        self,
        member_id: str,
        organization_id: str | None = None,
    ) -> Member | None:
        """
        Retrieve a member by their ID.

        Args:
            member_id: The membership's unique identifier.
            organization_id: Optional organization ID for tenant isolation.

        Returns:
            Member | None: The member if found, None otherwise.
        """
        query = select(Member).where(Member.id == member_id)

        if organization_id:
            query = query.where(Member.organization_id == organization_id)

        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_by_id_or_raise(
        self,
        member_id: str,
        organization_id: str | None = None,
    ) -> Member:
        """
        Retrieve a member by their ID or raise NotFoundError.

        Args:
            member_id: The membership's unique identifier.
            organization_id: Optional organization ID for tenant isolation.

        Returns:
            Member: The member.

        Raises:
            NotFoundError: If the member is not found.
        """
        member = await self.get_by_id(member_id, organization_id)
        if not member:
            raise NotFoundError(resource="Member", resource_id=member_id)
        return member

    async def get_by_user_and_department(
        self,
        user_id: str,
        department_id: str,
    ) -> Member | None:
        """
        Retrieve a member by user ID and department ID.

        Args:
            user_id: The user's unique identifier.
            department_id: The department's unique identifier.

        Returns:
            Member | None: The member if found, None otherwise.
        """
        query = select(Member).where(
            Member.user_id == user_id,
            Member.department_id == department_id,
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_by_department(
        self,
        department_id: str,
        *,
        include_inactive: bool = False,
    ) -> list[Member]:
        """
        Retrieve all members of a department.

        Args:
            department_id: The department's unique identifier.
            include_inactive: Whether to include inactive members.

        Returns:
            list[Member]: List of members.
        """
        query = select(Member).where(Member.department_id == department_id)

        if not include_inactive:
            query = query.where(Member.status == MemberStatus.ACTIVE)

        query = query.options(selectinload(Member.user))
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_by_user(
        self,
        user_id: str,
        organization_id: str | None = None,
    ) -> list[Member]:
        """
        Retrieve all memberships for a user.

        Args:
            user_id: The user's unique identifier.
            organization_id: Optional organization ID for tenant isolation.

        Returns:
            list[Member]: List of memberships.
        """
        query = select(Member).where(Member.user_id == user_id)

        if organization_id:
            query = query.where(Member.organization_id == organization_id)

        query = query.options(selectinload(Member.department))
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_active_members_for_department(
        self,
        department_id: str,
    ) -> list[Member]:
        """
        Retrieve all active members of a department with user info.

        Args:
            department_id: The department's unique identifier.

        Returns:
            list[Member]: List of active members with user data loaded.
        """
        query = (
            select(Member)
            .where(
                Member.department_id == department_id,
                Member.status == MemberStatus.ACTIVE,
            )
            .options(
                selectinload(Member.user),
                selectinload(Member.availabilities),
            )
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def update(
        self,
        member_id: str,
        organization_id: str,
        **kwargs: Any,
    ) -> Member:
        """
        Update a membership.

        Args:
            member_id: The membership's unique identifier.
            organization_id: Organization ID for tenant isolation.
            **kwargs: Fields to update.

        Returns:
            Member: The updated membership.

        Raises:
            NotFoundError: If the member is not found.
        """
        member = await self.get_by_id_or_raise(member_id, organization_id)

        for key, value in kwargs.items():
            if hasattr(member, key):
                setattr(member, key, value)

        await self.session.flush()
        await self.session.refresh(member)
        return member

    async def delete(
        self,
        member_id: str,
        organization_id: str,
    ) -> bool:
        """
        Delete a membership.

        Args:
            member_id: The membership's unique identifier.
            organization_id: Organization ID for tenant isolation.

        Returns:
            bool: True if deleted, False if not found.
        """
        member = await self.get_by_id(member_id, organization_id)
        if not member:
            return False

        await self.session.delete(member)
        await self.session.flush()
        return True
