"""
Planning Repository.

Data access layer for Planning entities.
"""

from collections.abc import Sequence
from datetime import date

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.planning import Planning, PlanningStatus


class PlanningRepository:
    """Repository for Planning entity operations."""

    def __init__(self, session: AsyncSession) -> None:
        """
        Initialize the repository.

        Args:
            session: SQLAlchemy async session
        """
        self.session = session

    async def create(self, planning: Planning) -> Planning:
        """
        Create a new planning.

        Args:
            planning: Planning entity to create

        Returns:
            Created planning with generated ID
        """
        self.session.add(planning)
        await self.session.flush()
        return planning

    async def get_by_id(self, planning_id: str) -> Planning | None:
        """
        Get a planning by ID.

        Args:
            planning_id: UUID of the planning

        Returns:
            Planning entity or None if not found
        """
        result = await self.session.execute(
            select(Planning)
            .where(Planning.id == planning_id)
            .options(selectinload(Planning.assignments))
        )
        return result.scalar_one_or_none()

    async def get_by_id_and_organization(
        self, planning_id: str, organization_id: str
    ) -> Planning | None:
        """
        Get a planning by ID within an organization.

        Args:
            planning_id: UUID of the planning
            organization_id: UUID of the organization

        Returns:
            Planning entity or None if not found
        """
        result = await self.session.execute(
            select(Planning)
            .where(
                and_(
                    Planning.id == planning_id,
                    Planning.organization_id == organization_id,
                )
            )
            .options(selectinload(Planning.assignments))
        )
        return result.scalar_one_or_none()

    async def get_by_department_and_month(
        self,
        department_id: str,
        organization_id: str,
        month: date,
    ) -> Planning | None:
        """
        Get planning for a department and month.

        Args:
            department_id: UUID of the department
            organization_id: UUID of the organization
            month: First day of the month

        Returns:
            Planning entity or None if not found
        """
        result = await self.session.execute(
            select(Planning)
            .where(
                and_(
                    Planning.department_id == department_id,
                    Planning.organization_id == organization_id,
                    Planning.month == month,
                )
            )
            .options(selectinload(Planning.assignments))
        )
        return result.scalar_one_or_none()

    async def get_by_department(
        self,
        department_id: str,
        organization_id: str,
        status: PlanningStatus | None = None,
    ) -> Sequence[Planning]:
        """
        Get all plannings for a department.

        Args:
            department_id: UUID of the department
            organization_id: UUID of the organization
            status: Optional status filter

        Returns:
            List of plannings
        """
        query = select(Planning).where(
            and_(
                Planning.department_id == department_id,
                Planning.organization_id == organization_id,
            )
        )

        if status:
            query = query.where(Planning.status == status)

        query = query.order_by(Planning.month.desc())

        result = await self.session.execute(query)
        return result.scalars().all()

    async def update(self, planning: Planning) -> Planning:
        """
        Update an existing planning.

        Args:
            planning: Planning entity with updates

        Returns:
            Updated planning
        """
        await self.session.flush()
        return planning

    async def delete(self, planning: Planning) -> None:
        """
        Delete a planning and all its assignments.

        Args:
            planning: Planning entity to delete
        """
        await self.session.delete(planning)
        await self.session.flush()

    async def get_published_for_member(
        self,
        member_id: str,
        organization_id: str,
        start_month: date | None = None,
        end_month: date | None = None,
    ) -> Sequence[Planning]:
        """
        Get published plannings where a member has assignments.

        Args:
            member_id: UUID of the member
            organization_id: UUID of the organization
            start_month: Optional start month filter
            end_month: Optional end month filter

        Returns:
            List of published plannings
        """
        from app.models.planning_assignment import PlanningAssignment

        query = (
            select(Planning)
            .join(PlanningAssignment, Planning.id == PlanningAssignment.planning_id)
            .where(
                and_(
                    Planning.organization_id == organization_id,
                    Planning.status == PlanningStatus.PUBLISHED,
                    PlanningAssignment.member_id == member_id,
                )
            )
        )

        if start_month:
            query = query.where(Planning.month >= start_month)
        if end_month:
            query = query.where(Planning.month <= end_month)

        query = query.distinct().order_by(Planning.month.desc())

        result = await self.session.execute(query)
        return result.scalars().all()
