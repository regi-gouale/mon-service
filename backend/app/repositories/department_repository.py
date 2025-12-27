"""
Department Repository.

Data access layer for Department model operations.
Provides async CRUD operations with proper error handling.
"""

from datetime import date
from typing import Any

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.exceptions import AlreadyExistsError, NotFoundError
from app.models.department import Department


class DepartmentRepository:
    """
    Repository for Department data access operations.

    Provides async CRUD operations for Department model with proper
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
        name: str,
        created_by: str,
        description: str | None = None,
        settings: dict[str, Any] | None = None,
        availability_deadline_days: int = 7,
        is_active: bool = True,
    ) -> Department:
        """
        Create a new department.

        Args:
            organization_id: Organization this department belongs to.
            name: Department name (unique per organization).
            created_by: User ID who created the department.
            description: Optional department description.
            settings: Optional department-specific settings.
            availability_deadline_days: Days before deadline for availability.
            is_active: Whether the department is active.

        Returns:
            Department: The created department instance.

        Raises:
            AlreadyExistsError: If a department with the name already exists in the org.
        """
        department = Department(
            organization_id=organization_id,
            name=name,
            description=description,
            settings=settings or {},
            availability_deadline_days=availability_deadline_days,
            is_active=is_active,
            created_by=created_by,
        )

        try:
            self.session.add(department)
            await self.session.flush()
            await self.session.refresh(department)
            return department
        except IntegrityError as e:
            await self.session.rollback()
            if "unique" in str(e.orig).lower() or "duplicate" in str(e.orig).lower():
                raise AlreadyExistsError(
                    resource="Department",
                    field="name",
                    value=name,
                ) from e
            raise

    async def get_by_id(
        self,
        department_id: str,
        organization_id: str | None = None,
    ) -> Department | None:
        """
        Retrieve a department by its ID.

        Args:
            department_id: The department's unique identifier.
            organization_id: Optional organization ID for tenant isolation.

        Returns:
            Department | None: The department if found, None otherwise.
        """
        query = select(Department).where(Department.id == department_id)

        if organization_id:
            query = query.where(Department.organization_id == organization_id)

        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_by_id_or_raise(
        self,
        department_id: str,
        organization_id: str | None = None,
    ) -> Department:
        """
        Retrieve a department by its ID or raise NotFoundError.

        Args:
            department_id: The department's unique identifier.
            organization_id: Optional organization ID for tenant isolation.

        Returns:
            Department: The department.

        Raises:
            NotFoundError: If the department is not found.
        """
        department = await self.get_by_id(department_id, organization_id)
        if not department:
            raise NotFoundError(resource="Department", resource_id=department_id)
        return department

    async def get_by_organization(
        self,
        organization_id: str,
        *,
        include_inactive: bool = False,
    ) -> list[Department]:
        """
        Retrieve all departments for an organization.

        Args:
            organization_id: The organization's unique identifier.
            include_inactive: Whether to include inactive departments.

        Returns:
            list[Department]: List of departments.
        """
        query = select(Department).where(Department.organization_id == organization_id)

        if not include_inactive:
            query = query.where(Department.is_active.is_(True))

        query = query.order_by(Department.name)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_with_members(
        self,
        department_id: str,
        organization_id: str | None = None,
    ) -> Department | None:
        """
        Retrieve a department with its members loaded.

        Args:
            department_id: The department's unique identifier.
            organization_id: Optional organization ID for tenant isolation.

        Returns:
            Department | None: The department with members, None if not found.
        """
        query = (
            select(Department)
            .options(selectinload(Department.members))
            .where(Department.id == department_id)
        )

        if organization_id:
            query = query.where(Department.organization_id == organization_id)

        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def update(
        self,
        department_id: str,
        organization_id: str,
        **kwargs: Any,
    ) -> Department:
        """
        Update a department.

        Args:
            department_id: The department's unique identifier.
            organization_id: Organization ID for tenant isolation.
            **kwargs: Fields to update.

        Returns:
            Department: The updated department.

        Raises:
            NotFoundError: If the department is not found.
            AlreadyExistsError: If name update conflicts with existing department.
        """
        department = await self.get_by_id_or_raise(department_id, organization_id)

        for key, value in kwargs.items():
            if hasattr(department, key):
                setattr(department, key, value)

        try:
            await self.session.flush()
            await self.session.refresh(department)
            return department
        except IntegrityError as e:
            await self.session.rollback()
            if "unique" in str(e.orig).lower():
                raise AlreadyExistsError(
                    resource="Department",
                    field="name",
                    value=kwargs.get("name", ""),
                ) from e
            raise

    async def delete(
        self,
        department_id: str,
        organization_id: str,
    ) -> bool:
        """
        Delete a department.

        Args:
            department_id: The department's unique identifier.
            organization_id: Organization ID for tenant isolation.

        Returns:
            bool: True if deleted, False if not found.
        """
        department = await self.get_by_id(department_id, organization_id)
        if not department:
            return False

        await self.session.delete(department)
        await self.session.flush()
        return True

    async def get_deadline_for_month(
        self,
        department_id: str,
        month: date,
    ) -> date:
        """
        Calculate the availability submission deadline for a given month.

        Args:
            department_id: The department's unique identifier.
            month: The first day of the target month.

        Returns:
            date: The deadline date for availability submission.

        Raises:
            NotFoundError: If the department is not found.
        """
        department = await self.get_by_id_or_raise(department_id)

        # Deadline is X days before the first day of the month
        from datetime import timedelta

        deadline = month - timedelta(days=department.availability_deadline_days)
        return deadline
