"""
Availability Service.

Business logic for managing member availability/unavailability.
Handles deadline validation, availability submission, and querying.
"""

from datetime import date, timedelta

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ForbiddenError, NotFoundError
from app.models.availability import Availability
from app.models.member import Member
from app.repositories.availability_repository import AvailabilityRepository
from app.repositories.department_repository import DepartmentRepository
from app.repositories.member_repository import MemberRepository
from app.schemas.availability import (
    AvailabilityDeadlineResponse,
    DepartmentAvailabilityResponse,
    MemberAvailabilityResponse,
)


class AvailabilityService:
    """
    Service for managing member availability.

    Provides business logic for:
    - Setting member unavailable dates
    - Checking availability deadlines
    - Querying availability for planning

    Attributes:
        session: The async database session.
    """

    def __init__(self, session: AsyncSession) -> None:
        """
        Initialize the service with a database session.

        Args:
            session: Async SQLAlchemy session for database operations.
        """
        self.session = session
        self.availability_repo = AvailabilityRepository(session)
        self.department_repo = DepartmentRepository(session)
        self.member_repo = MemberRepository(session)

    async def check_deadline(
        self,
        department_id: str,
        year: int,
        month: int,
    ) -> AvailabilityDeadlineResponse:
        """
        Check the availability submission deadline for a department/month.

        Args:
            department_id: The department's unique identifier.
            year: The target year.
            month: The target month (1-12).

        Returns:
            AvailabilityDeadlineResponse: Deadline information.

        Raises:
            NotFoundError: If the department is not found.
        """
        department = await self.department_repo.get_by_id_or_raise(department_id)

        # Calculate the first day of the target month
        first_day_of_month = date(year, month, 1)

        # Deadline is X days before the first day of the month
        deadline = first_day_of_month - timedelta(
            days=department.availability_deadline_days
        )

        today = date.today()
        is_past_deadline = today > deadline
        days_remaining = None if is_past_deadline else (deadline - today).days

        return AvailabilityDeadlineResponse(
            department_id=department.id,
            year=year,
            month=month,
            deadline=deadline,
            deadline_days=department.availability_deadline_days,
            is_past_deadline=is_past_deadline,
            days_remaining=days_remaining,
        )

    async def validate_deadline_not_passed(
        self,
        department_id: str,
        year: int,
        month: int,
    ) -> None:
        """
        Validate that the availability deadline has not passed.

        Args:
            department_id: The department's unique identifier.
            year: The target year.
            month: The target month (1-12).

        Raises:
            ForbiddenError: If the deadline has passed.
            NotFoundError: If the department is not found.
        """
        deadline_info = await self.check_deadline(department_id, year, month)

        if deadline_info.is_past_deadline:
            raise ForbiddenError(
                message=f"Availability submission deadline has passed. "
                f"Deadline was {deadline_info.deadline.isoformat()}."
            )

    async def set_member_availabilities(
        self,
        user_id: str,
        department_id: str,
        year: int,
        month: int,
        unavailable_dates: list[date],
        *,
        bypass_deadline: bool = False,
    ) -> list[Availability]:
        """
        Set the unavailable dates for a member in a given month.

        Args:
            user_id: The user's unique identifier.
            department_id: The department's unique identifier.
            year: The target year.
            month: The target month (1-12).
            unavailable_dates: List of dates the member is unavailable.
            bypass_deadline: If True, skip deadline validation (for admins).

        Returns:
            list[Availability]: List of created availability entries.

        Raises:
            NotFoundError: If the member or department is not found.
            ForbiddenError: If the deadline has passed.
        """
        # Get the member
        member = await self.member_repo.get_by_user_and_department(
            user_id=user_id,
            department_id=department_id,
        )
        if not member:
            raise NotFoundError(
                resource="Member",
                resource_id=f"user {user_id} in department {department_id}",
            )

        # Validate deadline unless bypassed
        if not bypass_deadline:
            await self.validate_deadline_not_passed(department_id, year, month)

        # Filter dates to only include dates in the specified month
        valid_dates = [
            d for d in unavailable_dates if d.year == year and d.month == month
        ]

        # Set the availabilities
        availabilities = await self.availability_repo.set_member_availabilities(
            organization_id=member.organization_id,
            member_id=member.id,
            year=year,
            month=month,
            unavailable_dates=valid_dates,
        )

        return availabilities

    async def get_member_availabilities(
        self,
        user_id: str,
        department_id: str,
        year: int,
        month: int,
    ) -> MemberAvailabilityResponse:
        """
        Get the unavailable dates for a member in a given month.

        Args:
            user_id: The user's unique identifier.
            department_id: The department's unique identifier.
            year: The target year.
            month: The target month (1-12).

        Returns:
            MemberAvailabilityResponse: Member's availability for the month.

        Raises:
            NotFoundError: If the member is not found.
        """
        # Get the member with user info
        member = await self.member_repo.get_by_user_and_department(
            user_id=user_id,
            department_id=department_id,
        )
        if not member:
            raise NotFoundError(
                resource="Member",
                resource_id=f"user {user_id} in department {department_id}",
            )

        # Get availability entries
        availabilities = await self.availability_repo.get_by_member_for_month(
            member_id=member.id,
            year=year,
            month=month,
        )

        return MemberAvailabilityResponse(
            member_id=member.id,
            member_name=f"{member.user.first_name} {member.user.last_name}",
            year=year,
            month=month,
            unavailable_dates=[a.date for a in availabilities],
        )

    async def get_department_availabilities(
        self,
        department_id: str,
        year: int,
        month: int,
    ) -> DepartmentAvailabilityResponse:
        """
        Get the availability overview for all members of a department.

        Args:
            department_id: The department's unique identifier.
            year: The target year.
            month: The target month (1-12).

        Returns:
            DepartmentAvailabilityResponse: Department-wide availability.

        Raises:
            NotFoundError: If the department is not found.
        """
        # Get department
        department = await self.department_repo.get_by_id_or_raise(department_id)

        # Get deadline info
        deadline_info = await self.check_deadline(department_id, year, month)

        # Get all active members
        members = await self.member_repo.get_active_members_for_department(
            department_id
        )

        # Get availabilities for each member
        member_availabilities = []
        for member in members:
            availabilities = await self.availability_repo.get_by_member_for_month(
                member_id=member.id,
                year=year,
                month=month,
            )
            member_availabilities.append(
                MemberAvailabilityResponse(
                    member_id=member.id,
                    member_name=f"{member.user.first_name} {member.user.last_name}",
                    year=year,
                    month=month,
                    unavailable_dates=[a.date for a in availabilities],
                )
            )

        return DepartmentAvailabilityResponse(
            department_id=department.id,
            department_name=department.name,
            year=year,
            month=month,
            deadline=deadline_info.deadline,
            deadline_passed=deadline_info.is_past_deadline,
            members=member_availabilities,
        )

    async def get_available_members_for_date(
        self,
        department_id: str,
        target_date: date,
    ) -> list[Member]:
        """
        Get all members who are available on a specific date.

        Args:
            department_id: The department's unique identifier.
            target_date: The date to check availability for.

        Returns:
            list[Member]: List of available members.
        """
        # Get all active members
        members = await self.member_repo.get_active_members_for_department(
            department_id
        )

        # Filter to only available members
        available_members = []
        for member in members:
            is_available = await self.availability_repo.check_member_available_on_date(
                member_id=member.id,
                check_date=target_date,
            )
            if is_available:
                available_members.append(member)

        return available_members

    async def check_member_available_on_date(
        self,
        member_id: str,
        target_date: date,
    ) -> bool:
        """
        Check if a specific member is available on a date.

        Args:
            member_id: The member's unique identifier.
            target_date: The date to check.

        Returns:
            bool: True if available, False if unavailable.
        """
        return await self.availability_repo.check_member_available_on_date(
            member_id=member_id,
            check_date=target_date,
        )
