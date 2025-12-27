"""
Service Repository.

Data access layer for Service entities.
"""

from collections.abc import Sequence
from datetime import date

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.service import Service


class ServiceRepository:
    """Repository for Service entity operations."""

    def __init__(self, session: AsyncSession) -> None:
        """
        Initialize the repository.

        Args:
            session: SQLAlchemy async session
        """
        self.session = session

    async def create(self, service: Service) -> Service:
        """
        Create a new service.

        Args:
            service: Service entity to create

        Returns:
            Created service with generated ID
        """
        self.session.add(service)
        await self.session.flush()
        return service

    async def get_by_id(self, service_id: str) -> Service | None:
        """
        Get a service by ID.

        Args:
            service_id: UUID of the service

        Returns:
            Service entity or None if not found
        """
        result = await self.session.execute(
            select(Service).where(Service.id == service_id)
        )
        return result.scalar_one_or_none()

    async def get_by_id_and_organization(
        self, service_id: str, organization_id: str
    ) -> Service | None:
        """
        Get a service by ID within an organization.

        Args:
            service_id: UUID of the service
            organization_id: UUID of the organization

        Returns:
            Service entity or None if not found
        """
        result = await self.session.execute(
            select(Service).where(
                and_(
                    Service.id == service_id,
                    Service.organization_id == organization_id,
                )
            )
        )
        return result.scalar_one_or_none()

    async def get_by_department(
        self,
        department_id: str,
        organization_id: str,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> Sequence[Service]:
        """
        Get all services for a department within a date range.

        Args:
            department_id: UUID of the department
            organization_id: UUID of the organization
            start_date: Optional start date filter
            end_date: Optional end date filter

        Returns:
            List of services
        """
        query = select(Service).where(
            and_(
                Service.department_id == department_id,
                Service.organization_id == organization_id,
            )
        )

        if start_date:
            query = query.where(Service.date >= start_date)
        if end_date:
            query = query.where(Service.date <= end_date)

        query = query.order_by(Service.date, Service.start_time)

        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_by_month(
        self,
        department_id: str,
        organization_id: str,
        year: int,
        month: int,
    ) -> Sequence[Service]:
        """
        Get all services for a department in a specific month.

        Args:
            department_id: UUID of the department
            organization_id: UUID of the organization
            year: Year
            month: Month (1-12)

        Returns:
            List of services
        """
        from calendar import monthrange

        start_date = date(year, month, 1)
        _, last_day = monthrange(year, month)
        end_date = date(year, month, last_day)

        return await self.get_by_department(
            department_id, organization_id, start_date, end_date
        )

    async def update(self, service: Service) -> Service:
        """
        Update an existing service.

        Args:
            service: Service entity with updates

        Returns:
            Updated service
        """
        await self.session.flush()
        return service

    async def delete(self, service: Service) -> None:
        """
        Delete a service.

        Args:
            service: Service entity to delete
        """
        await self.session.delete(service)
        await self.session.flush()

    async def get_services_by_date(
        self,
        department_id: str,
        organization_id: str,
        service_date: date,
    ) -> Sequence[Service]:
        """
        Get all services for a specific date.

        Args:
            department_id: UUID of the department
            organization_id: UUID of the organization
            service_date: Date to query

        Returns:
            List of services on that date
        """
        result = await self.session.execute(
            select(Service)
            .where(
                and_(
                    Service.department_id == department_id,
                    Service.organization_id == organization_id,
                    Service.date == service_date,
                )
            )
            .order_by(Service.start_time)
        )
        return result.scalars().all()
