"""
PlanningAssignment Repository.

Data access layer for PlanningAssignment entities.
"""

from collections.abc import Sequence
from datetime import date

from sqlalchemy import and_, delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.planning_assignment import AssignmentStatus, PlanningAssignment


class PlanningAssignmentRepository:
    """Repository for PlanningAssignment entity operations."""

    def __init__(self, session: AsyncSession) -> None:
        """
        Initialize the repository.

        Args:
            session: SQLAlchemy async session
        """
        self.session = session

    async def create(self, assignment: PlanningAssignment) -> PlanningAssignment:
        """
        Create a new assignment.

        Args:
            assignment: Assignment entity to create

        Returns:
            Created assignment with generated ID
        """
        self.session.add(assignment)
        await self.session.flush()
        return assignment

    async def create_bulk(
        self, assignments: list[PlanningAssignment]
    ) -> list[PlanningAssignment]:
        """
        Create multiple assignments in bulk.

        Args:
            assignments: List of assignment entities to create

        Returns:
            List of created assignments
        """
        self.session.add_all(assignments)
        await self.session.flush()
        return assignments

    async def get_by_id(self, assignment_id: str) -> PlanningAssignment | None:
        """
        Get an assignment by ID.

        Args:
            assignment_id: UUID of the assignment

        Returns:
            Assignment entity or None if not found
        """
        result = await self.session.execute(
            select(PlanningAssignment)
            .where(PlanningAssignment.id == assignment_id)
            .options(
                selectinload(PlanningAssignment.member),
                selectinload(PlanningAssignment.service),
            )
        )
        return result.scalar_one_or_none()

    async def get_by_planning(
        self,
        planning_id: str,
        organization_id: str,
    ) -> Sequence[PlanningAssignment]:
        """
        Get all assignments for a planning.

        Args:
            planning_id: UUID of the planning
            organization_id: UUID of the organization

        Returns:
            List of assignments
        """
        result = await self.session.execute(
            select(PlanningAssignment)
            .where(
                and_(
                    PlanningAssignment.planning_id == planning_id,
                    PlanningAssignment.organization_id == organization_id,
                )
            )
            .options(
                selectinload(PlanningAssignment.member),
                selectinload(PlanningAssignment.service),
            )
        )
        return result.scalars().all()

    async def get_by_service(
        self,
        service_id: str,
        organization_id: str,
    ) -> Sequence[PlanningAssignment]:
        """
        Get all assignments for a service.

        Args:
            service_id: UUID of the service
            organization_id: UUID of the organization

        Returns:
            List of assignments
        """
        result = await self.session.execute(
            select(PlanningAssignment)
            .where(
                and_(
                    PlanningAssignment.service_id == service_id,
                    PlanningAssignment.organization_id == organization_id,
                )
            )
            .options(selectinload(PlanningAssignment.member))
        )
        return result.scalars().all()

    async def get_by_member(
        self,
        member_id: str,
        organization_id: str,
        status: AssignmentStatus | None = None,
    ) -> Sequence[PlanningAssignment]:
        """
        Get all assignments for a member.

        Args:
            member_id: UUID of the member
            organization_id: UUID of the organization
            status: Optional status filter

        Returns:
            List of assignments
        """
        query = select(PlanningAssignment).where(
            and_(
                PlanningAssignment.member_id == member_id,
                PlanningAssignment.organization_id == organization_id,
            )
        )

        if status:
            query = query.where(PlanningAssignment.status == status)

        result = await self.session.execute(
            query.options(selectinload(PlanningAssignment.service))
        )
        return result.scalars().all()

    async def get_member_assignment_count(
        self,
        member_id: str,
        organization_id: str,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> int:
        """
        Count assignments for a member within a date range.

        Used for equity calculations in planning generation.

        Args:
            member_id: UUID of the member
            organization_id: UUID of the organization
            start_date: Optional start date
            end_date: Optional end date

        Returns:
            Number of assignments
        """
        from app.models.service import Service

        query = (
            select(func.count(PlanningAssignment.id))
            .join(Service, PlanningAssignment.service_id == Service.id)
            .where(
                and_(
                    PlanningAssignment.member_id == member_id,
                    PlanningAssignment.organization_id == organization_id,
                )
            )
        )

        if start_date:
            query = query.where(Service.date >= start_date)
        if end_date:
            query = query.where(Service.date <= end_date)

        result = await self.session.execute(query)
        return result.scalar() or 0

    async def update(self, assignment: PlanningAssignment) -> PlanningAssignment:
        """
        Update an existing assignment.

        Args:
            assignment: Assignment entity with updates

        Returns:
            Updated assignment
        """
        await self.session.flush()
        return assignment

    async def delete(self, assignment: PlanningAssignment) -> None:
        """
        Delete an assignment.

        Args:
            assignment: Assignment entity to delete
        """
        await self.session.delete(assignment)
        await self.session.flush()

    async def delete_by_planning(
        self,
        planning_id: str,
        organization_id: str,
    ) -> int:
        """
        Delete all assignments for a planning.

        Args:
            planning_id: UUID of the planning
            organization_id: UUID of the organization

        Returns:
            Number of deleted assignments
        """
        result = await self.session.execute(
            delete(PlanningAssignment).where(
                and_(
                    PlanningAssignment.planning_id == planning_id,
                    PlanningAssignment.organization_id == organization_id,
                )
            )
        )
        await self.session.flush()
        return int(result.rowcount) if result.rowcount else 0  # type: ignore[attr-defined]

    async def get_by_service_and_member(
        self,
        service_id: str,
        member_id: str,
    ) -> PlanningAssignment | None:
        """
        Check if a member is already assigned to a service.

        Args:
            service_id: UUID of the service
            member_id: UUID of the member

        Returns:
            Assignment if exists, None otherwise
        """
        result = await self.session.execute(
            select(PlanningAssignment).where(
                and_(
                    PlanningAssignment.service_id == service_id,
                    PlanningAssignment.member_id == member_id,
                )
            )
        )
        return result.scalar_one_or_none()
