"""
Integration Tests for Availability API Routes.

Tests for availability endpoints including getting and setting
member availabilities, checking deadlines, and department overview.
"""

from datetime import date, timedelta
from unittest.mock import AsyncMock, patch

import pytest
from fastapi import status
from httpx import ASGITransport, AsyncClient

from app.api.v1.dependencies import get_current_user
from app.main import app
from app.models.department import Department
from app.models.member import Member, MemberRole, MemberStatus
from app.models.user import User, UserRole
from app.schemas.availability import (
    AvailabilityDeadlineResponse,
    DepartmentAvailabilityResponse,
    MemberAvailabilityResponse,
)

# ============================================================================
# Fixtures
# ============================================================================


@pytest.fixture
def sample_user() -> User:
    """Create a sample user for testing."""
    return User(
        id="user-123",
        email="test@example.com",
        first_name="John",
        last_name="Doe",
        role=UserRole.MEMBER,
        is_active=True,
    )


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
def sample_deadline_response(
    sample_department: Department,
) -> AvailabilityDeadlineResponse:
    """Create a sample deadline response."""
    today = date.today()
    target_month = today.month + 2 if today.month <= 10 else (today.month - 10)
    target_year = today.year if today.month <= 10 else today.year + 1
    first_of_month = date(target_year, target_month, 1)
    deadline = first_of_month - timedelta(days=7)

    return AvailabilityDeadlineResponse(
        department_id=sample_department.id,
        year=target_year,
        month=target_month,
        deadline=deadline,
        deadline_days=7,
        is_past_deadline=False,
        days_remaining=30,
    )


@pytest.fixture
def sample_member_availability_response(
    sample_member: Member,
) -> MemberAvailabilityResponse:
    """Create a sample member availability response."""
    today = date.today()
    target_month = today.month + 2 if today.month <= 10 else (today.month - 10)
    target_year = today.year if today.month <= 10 else today.year + 1

    return MemberAvailabilityResponse(
        member_id=sample_member.id,
        member_name="John Doe",
        year=target_year,
        month=target_month,
        unavailable_dates=[
            date(target_year, target_month, 10),
            date(target_year, target_month, 15),
        ],
    )


@pytest.fixture
def sample_department_availability_response(
    sample_department: Department,
    sample_member_availability_response: MemberAvailabilityResponse,
    sample_deadline_response: AvailabilityDeadlineResponse,
) -> DepartmentAvailabilityResponse:
    """Create a sample department availability response."""
    return DepartmentAvailabilityResponse(
        department_id=sample_department.id,
        department_name=sample_department.name,
        year=sample_deadline_response.year,
        month=sample_deadline_response.month,
        deadline=sample_deadline_response.deadline,
        deadline_passed=False,
        members=[sample_member_availability_response],
    )


@pytest.fixture
async def async_client():
    """Create an async HTTP client for testing."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


@pytest.fixture
def override_auth(sample_user: User):
    """Override authentication dependency."""

    async def mock_get_current_user():
        return sample_user

    app.dependency_overrides[get_current_user] = mock_get_current_user
    yield
    app.dependency_overrides.clear()


# ============================================================================
# Tests: GET /departments/{id}/availabilities/deadline
# ============================================================================


class TestGetAvailabilityDeadline:
    """Tests for GET /api/v1/departments/{id}/availabilities/deadline."""

    @pytest.mark.asyncio
    async def test_get_deadline_success(
        self,
        async_client: AsyncClient,
        override_auth,  # noqa: ARG002
        sample_deadline_response: AvailabilityDeadlineResponse,
    ) -> None:
        """Test successfully getting availability deadline."""
        with patch(
            "app.api.v1.routes.availabilities.AvailabilityService.check_deadline",
            new_callable=AsyncMock,
            return_value=sample_deadline_response,
        ):
            response = await async_client.get(
                "/api/v1/departments/dept-123/availabilities/deadline",
                params={
                    "year": sample_deadline_response.year,
                    "month": sample_deadline_response.month,
                },
            )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["departmentId"] == "dept-123"
        assert data["isPastDeadline"] is False
        assert "deadline" in data

    @pytest.mark.asyncio
    async def test_get_deadline_unauthorized(
        self,
        async_client: AsyncClient,
    ) -> None:
        """Test getting deadline without authentication."""
        response = await async_client.get(
            "/api/v1/departments/dept-123/availabilities/deadline",
            params={"year": 2025, "month": 6},
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


# ============================================================================
# Tests: GET /departments/{id}/members/me/availabilities
# ============================================================================


class TestGetMyAvailabilities:
    """Tests for GET /api/v1/departments/{id}/members/me/availabilities."""

    @pytest.mark.asyncio
    async def test_get_my_availabilities_success(
        self,
        async_client: AsyncClient,
        override_auth,  # noqa: ARG002
        sample_member_availability_response: MemberAvailabilityResponse,
    ) -> None:
        """Test successfully getting my availabilities."""
        with patch(
            "app.api.v1.routes.availabilities.AvailabilityService.get_member_availabilities",
            new_callable=AsyncMock,
            return_value=sample_member_availability_response,
        ):
            response = await async_client.get(
                "/api/v1/departments/dept-123/members/me/availabilities",
                params={
                    "year": sample_member_availability_response.year,
                    "month": sample_member_availability_response.month,
                },
            )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["memberId"] == sample_member_availability_response.member_id
        assert data["memberName"] == sample_member_availability_response.member_name
        assert "unavailableDates" in data
        assert len(data["unavailableDates"]) == 2

    @pytest.mark.asyncio
    async def test_get_my_availabilities_unauthorized(
        self,
        async_client: AsyncClient,
    ) -> None:
        """Test getting my availabilities without authentication."""
        response = await async_client.get(
            "/api/v1/departments/dept-123/members/me/availabilities",
            params={"year": 2025, "month": 6},
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


# ============================================================================
# Tests: PUT /departments/{id}/members/me/availabilities
# ============================================================================


class TestSetMyAvailabilities:
    """Tests for PUT /api/v1/departments/{id}/members/me/availabilities."""

    @pytest.mark.asyncio
    async def test_set_my_availabilities_success(
        self,
        async_client: AsyncClient,
        override_auth,  # noqa: ARG002
        sample_member_availability_response: MemberAvailabilityResponse,
    ) -> None:
        """Test successfully setting my availabilities."""
        with (
            patch(
                "app.api.v1.routes.availabilities.AvailabilityService.set_member_availabilities",
                new_callable=AsyncMock,
                return_value=[],
            ),
            patch(
                "app.api.v1.routes.availabilities.AvailabilityService.get_member_availabilities",
                new_callable=AsyncMock,
                return_value=sample_member_availability_response,
            ),
        ):
            response = await async_client.put(
                "/api/v1/departments/dept-123/members/me/availabilities",
                json={
                    "year": sample_member_availability_response.year,
                    "month": sample_member_availability_response.month,
                    "unavailableDates": [
                        "2025-06-10",
                        "2025-06-15",
                    ],
                },
            )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "memberId" in data
        assert "unavailableDates" in data

    @pytest.mark.asyncio
    async def test_set_my_availabilities_unauthorized(
        self,
        async_client: AsyncClient,
    ) -> None:
        """Test setting my availabilities without authentication."""
        response = await async_client.put(
            "/api/v1/departments/dept-123/members/me/availabilities",
            json={
                "year": 2025,
                "month": 6,
                "unavailableDates": [],
            },
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


# ============================================================================
# Tests: GET /departments/{id}/availabilities
# ============================================================================


class TestGetDepartmentAvailabilities:
    """Tests for GET /api/v1/departments/{id}/availabilities."""

    @pytest.mark.asyncio
    async def test_get_department_availabilities_success(
        self,
        async_client: AsyncClient,
        override_auth,  # noqa: ARG002
        sample_department_availability_response: DepartmentAvailabilityResponse,
    ) -> None:
        """Test successfully getting department availabilities."""
        with patch(
            "app.api.v1.routes.availabilities.AvailabilityService.get_department_availabilities",
            new_callable=AsyncMock,
            return_value=sample_department_availability_response,
        ):
            response = await async_client.get(
                "/api/v1/departments/dept-123/availabilities",
                params={
                    "year": sample_department_availability_response.year,
                    "month": sample_department_availability_response.month,
                },
            )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["departmentId"] == "dept-123"
        assert (
            data["departmentName"]
            == sample_department_availability_response.department_name
        )
        assert "members" in data
        assert len(data["members"]) == 1

    @pytest.mark.asyncio
    async def test_get_department_availabilities_unauthorized(
        self,
        async_client: AsyncClient,
    ) -> None:
        """Test getting department availabilities without authentication."""
        response = await async_client.get(
            "/api/v1/departments/dept-123/availabilities",
            params={"year": 2025, "month": 6},
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
