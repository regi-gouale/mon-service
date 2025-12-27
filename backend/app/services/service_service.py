"""
Service Service.

Business logic for service (event) management.
"""

from datetime import date, time
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError, ValidationError
from app.models.service import Service
from app.repositories.department_repository import DepartmentRepository
from app.repositories.service_repository import ServiceRepository


class ServiceService:
    """Service for managing services/events."""

    def __init__(self, session: AsyncSession) -> None:
        """
        Initialize the service.

        Args:
            session: SQLAlchemy async session
        """
        self.session = session
        self.service_repo = ServiceRepository(session)
        self.department_repo = DepartmentRepository(session)

    async def create_service(
        self,
        organization_id: str,
        department_id: str,
        name: str,
        service_type: str,
        service_date: date,
        start_time: time,
        created_by: str,
        end_time: time | None = None,
        location: str | None = None,
        dress_code_id: str | None = None,
        required_roles: list[dict[str, Any]] | None = None,
        notes: str | None = None,
        is_recurring: bool = False,
        recurrence_rule: str | None = None,
    ) -> Service:
        """
        Create a new service.

        Args:
            organization_id: UUID of the organization
            department_id: UUID of the department
            name: Name of the service
            service_type: Type (culte, répétition, événement)
            service_date: Date of the service
            start_time: Start time
            created_by: UUID of the creator
            end_time: Optional end time
            location: Optional location
            dress_code_id: Optional dress code ID
            required_roles: Required roles with counts
            notes: Optional notes
            is_recurring: Whether recurring
            recurrence_rule: RRULE for recurring services

        Returns:
            Created service

        Raises:
            NotFoundError: If department not found
            ValidationError: If validation fails
        """
        # Verify department exists
        department = await self.department_repo.get_by_id(department_id)
        if not department or department.organization_id != organization_id:
            raise NotFoundError("Department", department_id)

        # Validate times
        if end_time and start_time >= end_time:
            raise ValidationError("Start time must be before end time")

        # Validate required_roles format
        if required_roles:
            for role in required_roles:
                if not isinstance(role, dict) or "role" not in role:
                    raise ValidationError("Each required_role must have a 'role' field")
                if "count" in role and (
                    not isinstance(role["count"], int) or role["count"] < 1
                ):
                    raise ValidationError("Role count must be a positive integer")

        service = Service(
            organization_id=organization_id,
            department_id=department_id,
            name=name,
            service_type=service_type,
            date=service_date,
            start_time=start_time,
            end_time=end_time,
            location=location,
            dress_code_id=dress_code_id,
            required_roles=required_roles or [],
            notes=notes,
            is_recurring=is_recurring,
            recurrence_rule=recurrence_rule,
            created_by=created_by,
        )

        service = await self.service_repo.create(service)
        await self.session.commit()

        return service

    async def get_service(
        self,
        service_id: str,
        organization_id: str,
    ) -> Service:
        """
        Get a service by ID.

        Args:
            service_id: UUID of the service
            organization_id: UUID of the organization

        Returns:
            Service entity

        Raises:
            NotFoundError: If service not found
        """
        service = await self.service_repo.get_by_id_and_organization(
            service_id, organization_id
        )
        if not service:
            raise NotFoundError("Service", service_id)
        return service

    async def list_services(
        self,
        department_id: str,
        organization_id: str,
        year: int | None = None,
        month: int | None = None,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> list[Service]:
        """
        List services for a department.

        Args:
            department_id: UUID of the department
            organization_id: UUID of the organization
            year: Optional year filter
            month: Optional month filter
            start_date: Optional start date filter
            end_date: Optional end date filter

        Returns:
            List of services
        """
        if year and month:
            services = await self.service_repo.get_by_month(
                department_id, organization_id, year, month
            )
        else:
            services = await self.service_repo.get_by_department(
                department_id, organization_id, start_date, end_date
            )
        return list(services)

    async def update_service(
        self,
        service_id: str,
        organization_id: str,
        name: str | None = None,
        service_type: str | None = None,
        service_date: date | None = None,
        start_time: time | None = None,
        end_time: time | None = None,
        location: str | None = None,
        dress_code_id: str | None = None,
        required_roles: list[dict[str, Any]] | None = None,
        notes: str | None = None,
        is_recurring: bool | None = None,
        recurrence_rule: str | None = None,
    ) -> Service:
        """
        Update a service.

        Args:
            service_id: UUID of the service
            organization_id: UUID of the organization
            Various optional update fields

        Returns:
            Updated service

        Raises:
            NotFoundError: If service not found
        """
        service = await self.get_service(service_id, organization_id)

        if name is not None:
            service.name = name
        if service_type is not None:
            service.service_type = service_type
        if service_date is not None:
            service.date = service_date
        if start_time is not None:
            service.start_time = start_time
        if end_time is not None:
            service.end_time = end_time
        if location is not None:
            service.location = location
        if dress_code_id is not None:
            service.dress_code_id = dress_code_id
        if required_roles is not None:
            service.required_roles = required_roles
        if notes is not None:
            service.notes = notes
        if is_recurring is not None:
            service.is_recurring = is_recurring
        if recurrence_rule is not None:
            service.recurrence_rule = recurrence_rule

        # Validate times
        if service.end_time and service.start_time >= service.end_time:
            raise ValidationError("Start time must be before end time")

        await self.service_repo.update(service)
        await self.session.commit()

        return service

    async def delete_service(
        self,
        service_id: str,
        organization_id: str,
    ) -> None:
        """
        Delete a service.

        Args:
            service_id: UUID of the service
            organization_id: UUID of the organization

        Raises:
            NotFoundError: If service not found
        """
        service = await self.get_service(service_id, organization_id)
        await self.service_repo.delete(service)
        await self.session.commit()

    async def create_recurring_services(
        self,
        organization_id: str,
        department_id: str,
        name: str,
        service_type: str,
        start_time: time,
        created_by: str,
        start_date: date,
        end_date: date,
        recurrence_rule: str,
        end_time: time | None = None,
        location: str | None = None,
        required_roles: list[dict[str, Any]] | None = None,
        notes: str | None = None,
    ) -> list[Service]:
        """
        Create multiple services from a recurrence rule.

        This is a simplified implementation - for full RRULE support,
        consider using the python-dateutil library.

        Args:
            Various parameters for recurring service creation

        Returns:
            List of created services
        """
        from datetime import timedelta

        # Simple weekly recurrence for now
        services = []
        current_date = start_date

        while current_date <= end_date:
            service = Service(
                organization_id=organization_id,
                department_id=department_id,
                name=name,
                service_type=service_type,
                date=current_date,
                start_time=start_time,
                end_time=end_time,
                location=location,
                required_roles=required_roles or [],
                notes=notes,
                is_recurring=True,
                recurrence_rule=recurrence_rule,
                created_by=created_by,
            )
            await self.service_repo.create(service)
            services.append(service)

            # Move to next occurrence (weekly)
            current_date += timedelta(days=7)

        await self.session.commit()
        return services
