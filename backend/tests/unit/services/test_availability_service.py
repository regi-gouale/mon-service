"""
Unit Tests for AvailabilityService.

Tests for availability service business logic including
deadline validation, setting availabilities, and querying.
"""

from datetime import date, timedelta
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.core.exceptions import ForbiddenError, NotFoundError
from app.models.availability import Availability
from app.models.department import Department
from app.models.member import Member, MemberRole, MemberStatus
from app.models.user import User
from app.services.availability_service import AvailabilityService

# ============================================================================
# Fixtures
# ============================================================================


@pytest.fixture
def mock_session() -> AsyncMock:
    """Create a mock async session."""
    session = AsyncMock()
    session.commit = AsyncMock()
    session.flush = AsyncMock()
    session.rollback = AsyncMock()
    session.add = MagicMock()
    session.execute = AsyncMock()
    return session


@pytest.fixture
def availability_service(mock_session: AsyncMock) -> AvailabilityService:
    """Create an AvailabilityService instance with mock session."""
    return AvailabilityService(mock_session)


@pytest.fixture
def sample_department() -> Department:
    """Create a sample department for testing."""
    return Department(
        id="dept-123",
        organization_id="org-123",
        name="Music Team",
        description="Worship music team",
        availability_deadline_days=7,
        is_active=True,
        created_by="user-admin",
    )


@pytest.fixture
def sample_user() -> User:
    """Create a sample user for testing."""
    user = User(
        id="user-123",
        email="test@example.com",
        first_name="John",
        last_name="Doe",
        is_active=True,
    )
    return user


@pytest.fixture
def sample_member(sample_user: User, sample_department: Department) -> Member:
    """Create a sample member for testing."""
    member = Member(
        id="member-123",
        organization_id="org-123",
        department_id=sample_department.id,
        user_id=sample_user.id,
        role=MemberRole.MEMBER,
        status=MemberStatus.ACTIVE,
    )
    member.user = sample_user
    return member


@pytest.fixture
def sample_availabilities(sample_member: Member) -> list[Availability]:
    """Create sample availabilities for testing."""
    today = date.today()
    first_of_next_month = date(
        today.year, today.month + 1 if today.month < 12 else 1, 1
    )
    if today.month == 12:
        first_of_next_month = date(today.year + 1, 1, 1)

    return [
        Availability(
            id="avail-1",
            organization_id="org-123",
            member_id=sample_member.id,
            date=first_of_next_month + timedelta(days=5),
            reason="Vacation",
            is_all_day=True,
        ),
        Availability(
            id="avail-2",
            organization_id="org-123",
            member_id=sample_member.id,
            date=first_of_next_month + timedelta(days=12),
            reason="Family event",
            is_all_day=True,
        ),
    ]


# ============================================================================
# Tests: check_deadline
# ============================================================================


class TestCheckDeadline:
    """Tests for AvailabilityService.check_deadline method."""

    @pytest.mark.asyncio
    async def test_check_deadline_not_passed(
        self,
        availability_service: AvailabilityService,
        sample_department: Department,
    ) -> None:
        """Test deadline check when deadline has not passed."""
        # Mock department repo
        availability_service.department_repo.get_by_id_or_raise = AsyncMock(
            return_value=sample_department
        )

        # Use a future month
        today = date.today()
        target_month = today.month + 2 if today.month <= 10 else (today.month - 10)
        target_year = today.year if today.month <= 10 else today.year + 1

        result = await availability_service.check_deadline(
            department_id=sample_department.id,
            year=target_year,
            month=target_month,
        )

        assert result.department_id == sample_department.id
        assert result.year == target_year
        assert result.month == target_month
        assert result.deadline_days == sample_department.availability_deadline_days
        assert result.is_past_deadline is False
        assert result.days_remaining is not None
        assert result.days_remaining > 0

    @pytest.mark.asyncio
    async def test_check_deadline_passed(
        self,
        availability_service: AvailabilityService,
        sample_department: Department,
    ) -> None:
        """Test deadline check when deadline has passed."""
        # Mock department repo
        availability_service.department_repo.get_by_id_or_raise = AsyncMock(
            return_value=sample_department
        )

        # Use current month (deadline should be passed)
        today = date.today()

        result = await availability_service.check_deadline(
            department_id=sample_department.id,
            year=today.year,
            month=today.month,
        )

        assert result.is_past_deadline is True
        assert result.days_remaining is None

    @pytest.mark.asyncio
    async def test_check_deadline_department_not_found(
        self,
        availability_service: AvailabilityService,
    ) -> None:
        """Test deadline check when department is not found."""
        availability_service.department_repo.get_by_id_or_raise = AsyncMock(
            side_effect=NotFoundError(resource="Department", resource_id="not-found")
        )

        with pytest.raises(NotFoundError):
            await availability_service.check_deadline(
                department_id="not-found",
                year=2025,
                month=6,
            )


# ============================================================================
# Tests: validate_deadline_not_passed
# ============================================================================


class TestValidateDeadlineNotPassed:
    """Tests for AvailabilityService.validate_deadline_not_passed method."""

    @pytest.mark.asyncio
    async def test_validate_deadline_raises_when_passed(
        self,
        availability_service: AvailabilityService,
        sample_department: Department,
    ) -> None:
        """Test that ForbiddenError is raised when deadline has passed."""
        availability_service.department_repo.get_by_id_or_raise = AsyncMock(
            return_value=sample_department
        )

        today = date.today()

        with pytest.raises(ForbiddenError) as exc_info:
            await availability_service.validate_deadline_not_passed(
                department_id=sample_department.id,
                year=today.year,
                month=today.month,
            )

        assert "deadline has passed" in str(exc_info.value.message).lower()

    @pytest.mark.asyncio
    async def test_validate_deadline_passes_when_not_passed(
        self,
        availability_service: AvailabilityService,
        sample_department: Department,
    ) -> None:
        """Test that no error is raised when deadline has not passed."""
        availability_service.department_repo.get_by_id_or_raise = AsyncMock(
            return_value=sample_department
        )

        # Use a future month
        today = date.today()
        target_month = today.month + 2 if today.month <= 10 else (today.month - 10)
        target_year = today.year if today.month <= 10 else today.year + 1

        # Should not raise
        await availability_service.validate_deadline_not_passed(
            department_id=sample_department.id,
            year=target_year,
            month=target_month,
        )


# ============================================================================
# Tests: set_member_availabilities
# ============================================================================


class TestSetMemberAvailabilities:
    """Tests for AvailabilityService.set_member_availabilities method."""

    @pytest.mark.asyncio
    async def test_set_availabilities_success(
        self,
        availability_service: AvailabilityService,
        sample_department: Department,
        sample_member: Member,
        sample_availabilities: list[Availability],
    ) -> None:
        """Test successfully setting member availabilities."""
        # Mock repos
        availability_service.member_repo.get_by_user_and_department = AsyncMock(
            return_value=sample_member
        )
        availability_service.department_repo.get_by_id_or_raise = AsyncMock(
            return_value=sample_department
        )
        availability_service.availability_repo.set_member_availabilities = AsyncMock(
            return_value=sample_availabilities
        )

        # Use future dates to avoid deadline issues
        today = date.today()
        target_month = today.month + 2 if today.month <= 10 else (today.month - 10)
        target_year = today.year if today.month <= 10 else today.year + 1
        first_of_target = date(target_year, target_month, 1)

        unavailable_dates = [
            first_of_target + timedelta(days=5),
            first_of_target + timedelta(days=12),
        ]

        result = await availability_service.set_member_availabilities(
            user_id=sample_member.user_id,
            department_id=sample_department.id,
            year=target_year,
            month=target_month,
            unavailable_dates=unavailable_dates,
        )

        assert len(result) == len(sample_availabilities)
        availability_service.availability_repo.set_member_availabilities.assert_called_once()

    @pytest.mark.asyncio
    async def test_set_availabilities_member_not_found(
        self,
        availability_service: AvailabilityService,
    ) -> None:
        """Test setting availabilities when member is not found."""
        availability_service.member_repo.get_by_user_and_department = AsyncMock(
            return_value=None
        )

        with pytest.raises(NotFoundError) as exc_info:
            await availability_service.set_member_availabilities(
                user_id="unknown-user",
                department_id="dept-123",
                year=2025,
                month=6,
                unavailable_dates=[date(2025, 6, 15)],
            )

        assert "Member" in str(exc_info.value.message)

    @pytest.mark.asyncio
    async def test_set_availabilities_deadline_passed(
        self,
        availability_service: AvailabilityService,
        sample_department: Department,
        sample_member: Member,
    ) -> None:
        """Test that setting availabilities fails when deadline has passed."""
        availability_service.member_repo.get_by_user_and_department = AsyncMock(
            return_value=sample_member
        )
        availability_service.department_repo.get_by_id_or_raise = AsyncMock(
            return_value=sample_department
        )

        today = date.today()

        with pytest.raises(ForbiddenError):
            await availability_service.set_member_availabilities(
                user_id=sample_member.user_id,
                department_id=sample_department.id,
                year=today.year,
                month=today.month,
                unavailable_dates=[today + timedelta(days=1)],
            )

    @pytest.mark.asyncio
    async def test_set_availabilities_bypass_deadline(
        self,
        availability_service: AvailabilityService,
        sample_department: Department,
        sample_member: Member,
        sample_availabilities: list[Availability],
    ) -> None:
        """Test that bypass_deadline flag allows setting past deadline."""
        availability_service.member_repo.get_by_user_and_department = AsyncMock(
            return_value=sample_member
        )
        availability_service.department_repo.get_by_id_or_raise = AsyncMock(
            return_value=sample_department
        )
        availability_service.availability_repo.set_member_availabilities = AsyncMock(
            return_value=sample_availabilities
        )

        today = date.today()

        # Should not raise with bypass_deadline=True
        result = await availability_service.set_member_availabilities(
            user_id=sample_member.user_id,
            department_id=sample_department.id,
            year=today.year,
            month=today.month,
            unavailable_dates=[today + timedelta(days=1)],
            bypass_deadline=True,
        )

        assert result is not None

    @pytest.mark.asyncio
    async def test_set_availabilities_filters_wrong_month(
        self,
        availability_service: AvailabilityService,
        sample_department: Department,
        sample_member: Member,
    ) -> None:
        """Test that dates from wrong month are filtered out."""
        availability_service.member_repo.get_by_user_and_department = AsyncMock(
            return_value=sample_member
        )
        availability_service.department_repo.get_by_id_or_raise = AsyncMock(
            return_value=sample_department
        )
        availability_service.availability_repo.set_member_availabilities = AsyncMock(
            return_value=[]
        )

        today = date.today()
        target_month = today.month + 2 if today.month <= 10 else (today.month - 10)
        target_year = today.year if today.month <= 10 else today.year + 1

        # Include dates from wrong month
        wrong_month = target_month + 1 if target_month < 12 else 1
        wrong_year = target_year if target_month < 12 else target_year + 1

        unavailable_dates = [
            date(target_year, target_month, 15),  # correct month
            date(wrong_year, wrong_month, 15),  # wrong month
        ]

        await availability_service.set_member_availabilities(
            user_id=sample_member.user_id,
            department_id=sample_department.id,
            year=target_year,
            month=target_month,
            unavailable_dates=unavailable_dates,
        )

        # Check that only the valid date was passed
        call_args = (
            availability_service.availability_repo.set_member_availabilities.call_args
        )
        passed_dates = call_args.kwargs["unavailable_dates"]
        assert len(passed_dates) == 1
        assert passed_dates[0].month == target_month


# ============================================================================
# Tests: get_member_availabilities
# ============================================================================


class TestGetMemberAvailabilities:
    """Tests for AvailabilityService.get_member_availabilities method."""

    @pytest.mark.asyncio
    async def test_get_availabilities_success(
        self,
        availability_service: AvailabilityService,
        sample_member: Member,
        sample_availabilities: list[Availability],
    ) -> None:
        """Test successfully getting member availabilities."""
        availability_service.member_repo.get_by_user_and_department = AsyncMock(
            return_value=sample_member
        )
        availability_service.availability_repo.get_by_member_for_month = AsyncMock(
            return_value=sample_availabilities
        )

        result = await availability_service.get_member_availabilities(
            user_id=sample_member.user_id,
            department_id=sample_member.department_id,
            year=2025,
            month=6,
        )

        assert result.member_id == sample_member.id
        assert (
            result.member_name
            == f"{sample_member.user.first_name} {sample_member.user.last_name}"
        )
        assert len(result.unavailable_dates) == len(sample_availabilities)

    @pytest.mark.asyncio
    async def test_get_availabilities_member_not_found(
        self,
        availability_service: AvailabilityService,
    ) -> None:
        """Test getting availabilities when member is not found."""
        availability_service.member_repo.get_by_user_and_department = AsyncMock(
            return_value=None
        )

        with pytest.raises(NotFoundError):
            await availability_service.get_member_availabilities(
                user_id="unknown-user",
                department_id="dept-123",
                year=2025,
                month=6,
            )

    @pytest.mark.asyncio
    async def test_get_availabilities_empty(
        self,
        availability_service: AvailabilityService,
        sample_member: Member,
    ) -> None:
        """Test getting availabilities when none exist."""
        availability_service.member_repo.get_by_user_and_department = AsyncMock(
            return_value=sample_member
        )
        availability_service.availability_repo.get_by_member_for_month = AsyncMock(
            return_value=[]
        )

        result = await availability_service.get_member_availabilities(
            user_id=sample_member.user_id,
            department_id=sample_member.department_id,
            year=2025,
            month=6,
        )

        assert result.unavailable_dates == []


# ============================================================================
# Tests: get_department_availabilities
# ============================================================================


class TestGetDepartmentAvailabilities:
    """Tests for AvailabilityService.get_department_availabilities method."""

    @pytest.mark.asyncio
    async def test_get_department_availabilities_success(
        self,
        availability_service: AvailabilityService,
        sample_department: Department,
        sample_member: Member,
        sample_availabilities: list[Availability],
    ) -> None:
        """Test successfully getting department availabilities."""
        availability_service.department_repo.get_by_id_or_raise = AsyncMock(
            return_value=sample_department
        )
        availability_service.member_repo.get_active_members_for_department = AsyncMock(
            return_value=[sample_member]
        )
        availability_service.availability_repo.get_by_member_for_month = AsyncMock(
            return_value=sample_availabilities
        )

        result = await availability_service.get_department_availabilities(
            department_id=sample_department.id,
            year=2025,
            month=6,
        )

        assert result.department_id == sample_department.id
        assert result.department_name == sample_department.name
        assert result.year == 2025
        assert result.month == 6
        assert len(result.members) == 1

    @pytest.mark.asyncio
    async def test_get_department_availabilities_not_found(
        self,
        availability_service: AvailabilityService,
    ) -> None:
        """Test getting department availabilities when department not found."""
        availability_service.department_repo.get_by_id_or_raise = AsyncMock(
            side_effect=NotFoundError(resource="Department", resource_id="not-found")
        )

        with pytest.raises(NotFoundError):
            await availability_service.get_department_availabilities(
                department_id="not-found",
                year=2025,
                month=6,
            )
