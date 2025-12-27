"""
Availability Repository.

Data access layer for Availability model operations.
Provides async CRUD operations with proper error handling.
"""

from datetime import date, time

from sqlalchemy import delete, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.exceptions import AlreadyExistsError
from app.models.availability import Availability


class AvailabilityRepository:
    """
    Repository for Availability data access operations.

    Provides async CRUD operations for Availability model with proper
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
        member_id: str,
        availability_date: date,
        reason: str | None = None,
        is_all_day: bool = True,
        start_time: time | None = None,
        end_time: time | None = None,
    ) -> Availability:
        """
        Create a new availability entry (marks a date as unavailable).

        Args:
            organization_id: Organization this availability belongs to.
            member_id: Member marking the unavailability.
            availability_date: Date of unavailability.
            reason: Optional reason for unavailability.
            is_all_day: Whether the unavailability is for the entire day.
            start_time: Start time if partial day.
            end_time: End time if partial day.

        Returns:
            Availability: The created availability instance.

        Raises:
            AlreadyExistsError: If an availability entry already exists for this date.
        """
        availability = Availability(
            organization_id=organization_id,
            member_id=member_id,
            date=availability_date,
            reason=reason,
            is_all_day=is_all_day,
            start_time=start_time,
            end_time=end_time,
        )

        try:
            self.session.add(availability)
            await self.session.flush()
            await self.session.refresh(availability)
            return availability
        except IntegrityError as e:
            await self.session.rollback()
            if "unique" in str(e.orig).lower() or "duplicate" in str(e.orig).lower():
                raise AlreadyExistsError(
                    resource="Availability",
                    field="date",
                    value=str(availability_date),
                ) from e
            raise

    async def get_by_id(
        self,
        availability_id: str,
        organization_id: str | None = None,
    ) -> Availability | None:
        """
        Retrieve an availability entry by its ID.

        Args:
            availability_id: The availability's unique identifier.
            organization_id: Optional organization ID for tenant isolation.

        Returns:
            Availability | None: The availability if found, None otherwise.
        """
        query = select(Availability).where(Availability.id == availability_id)

        if organization_id:
            query = query.where(Availability.organization_id == organization_id)

        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_by_member_and_date(
        self,
        member_id: str,
        availability_date: date,
    ) -> Availability | None:
        """
        Retrieve an availability entry by member ID and date.

        Args:
            member_id: The member's unique identifier.
            availability_date: The date to check.

        Returns:
            Availability | None: The availability if found, None otherwise.
        """
        query = select(Availability).where(
            Availability.member_id == member_id,
            Availability.date == availability_date,
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_by_member_for_month(
        self,
        member_id: str,
        year: int,
        month: int,
    ) -> list[Availability]:
        """
        Retrieve all availability entries for a member in a given month.

        Args:
            member_id: The member's unique identifier.
            year: The year.
            month: The month (1-12).

        Returns:
            list[Availability]: List of availability entries.
        """
        from calendar import monthrange

        start_date = date(year, month, 1)
        _, last_day = monthrange(year, month)
        end_date = date(year, month, last_day)

        query = (
            select(Availability)
            .where(
                Availability.member_id == member_id,
                Availability.date >= start_date,
                Availability.date <= end_date,
            )
            .order_by(Availability.date)
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_by_member_for_date_range(
        self,
        member_id: str,
        start_date: date,
        end_date: date,
    ) -> list[Availability]:
        """
        Retrieve all availability entries for a member in a date range.

        Args:
            member_id: The member's unique identifier.
            start_date: Start of the date range (inclusive).
            end_date: End of the date range (inclusive).

        Returns:
            list[Availability]: List of availability entries.
        """
        query = (
            select(Availability)
            .where(
                Availability.member_id == member_id,
                Availability.date >= start_date,
                Availability.date <= end_date,
            )
            .order_by(Availability.date)
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_department_availabilities_for_month(
        self,
        department_id: str,
        year: int,
        month: int,
    ) -> list[Availability]:
        """
        Retrieve all availability entries for all members of a department in a month.

        Args:
            department_id: The department's unique identifier.
            year: The year.
            month: The month (1-12).

        Returns:
            list[Availability]: List of availability entries with member info.
        """
        from calendar import monthrange

        from app.models.member import Member

        start_date = date(year, month, 1)
        _, last_day = monthrange(year, month)
        end_date = date(year, month, last_day)

        query = (
            select(Availability)
            .join(Member, Availability.member_id == Member.id)
            .where(
                Member.department_id == department_id,
                Availability.date >= start_date,
                Availability.date <= end_date,
            )
            .options(selectinload(Availability.member))
            .order_by(Availability.date)
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def set_member_availabilities(
        self,
        organization_id: str,
        member_id: str,
        year: int,
        month: int,
        unavailable_dates: list[date],
    ) -> list[Availability]:
        """
        Set the unavailable dates for a member in a given month.

        This replaces all existing entries for the month with the new ones.

        Args:
            organization_id: Organization this availability belongs to.
            member_id: The member's unique identifier.
            year: The year.
            month: The month (1-12).
            unavailable_dates: List of dates the member is unavailable.

        Returns:
            list[Availability]: List of created availability entries.
        """
        from calendar import monthrange

        # Calculate month boundaries
        start_date = date(year, month, 1)
        _, last_day = monthrange(year, month)
        end_date = date(year, month, last_day)

        # Delete existing entries for this month
        delete_stmt = delete(Availability).where(
            Availability.member_id == member_id,
            Availability.date >= start_date,
            Availability.date <= end_date,
        )
        await self.session.execute(delete_stmt)

        # Create new entries for each unavailable date
        availabilities = []
        for unavailable_date in unavailable_dates:
            # Validate date is within the specified month
            if unavailable_date.year == year and unavailable_date.month == month:
                availability = Availability(
                    organization_id=organization_id,
                    member_id=member_id,
                    date=unavailable_date,
                    is_all_day=True,
                )
                self.session.add(availability)
                availabilities.append(availability)

        await self.session.flush()

        # Refresh to get generated IDs
        for availability in availabilities:
            await self.session.refresh(availability)

        return availabilities

    async def delete(
        self,
        availability_id: str,
        organization_id: str,
    ) -> bool:
        """
        Delete an availability entry.

        Args:
            availability_id: The availability's unique identifier.
            organization_id: Organization ID for tenant isolation.

        Returns:
            bool: True if deleted, False if not found.
        """
        availability = await self.get_by_id(availability_id, organization_id)
        if not availability:
            return False

        await self.session.delete(availability)
        await self.session.flush()
        return True

    async def delete_by_member_and_date(
        self,
        member_id: str,
        availability_date: date,
    ) -> bool:
        """
        Delete an availability entry by member ID and date.

        Args:
            member_id: The member's unique identifier.
            availability_date: The date to delete.

        Returns:
            bool: True if deleted, False if not found.
        """
        delete_stmt = delete(Availability).where(
            Availability.member_id == member_id,
            Availability.date == availability_date,
        )
        result = await self.session.execute(delete_stmt)
        await self.session.flush()
        # rowcount is available on CursorResult but mypy doesn't know that
        return bool(result.rowcount and result.rowcount > 0)  # type: ignore[attr-defined]

    async def check_member_available_on_date(
        self,
        member_id: str,
        check_date: date,
    ) -> bool:
        """
        Check if a member is available on a specific date.

        Args:
            member_id: The member's unique identifier.
            check_date: The date to check.

        Returns:
            bool: True if available (no unavailability entry), False if unavailable.
        """
        availability = await self.get_by_member_and_date(member_id, check_date)
        return availability is None
