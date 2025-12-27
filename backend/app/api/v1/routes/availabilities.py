"""
Availability API Routes.

REST endpoints for managing member availability/unavailability.
These routes are nested under departments.
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.dependencies import get_current_user
from app.core.database import get_db
from app.core.exceptions import ForbiddenError, NotFoundError
from app.core.logging import get_logger
from app.models.user import User
from app.schemas.availability import (
    AvailabilityDeadlineResponse,
    DepartmentAvailabilityResponse,
    MemberAvailabilityResponse,
    SetAvailabilitiesRequest,
)
from app.services.availability_service import AvailabilityService

logger = get_logger(__name__)

router = APIRouter(prefix="/departments", tags=["Availability"])

# Type aliases
DbSession = Annotated[AsyncSession, Depends(get_db)]
CurrentUser = Annotated[User, Depends(get_current_user)]


def get_availability_service(session: DbSession) -> AvailabilityService:
    """Get availability service instance."""
    return AvailabilityService(session)


AvailabilityServiceDep = Annotated[
    AvailabilityService, Depends(get_availability_service)
]


@router.get(
    "/{department_id}/availabilities",
    response_model=DepartmentAvailabilityResponse,
    summary="Get department availabilities",
    description="Get availability overview for all members of a department for a specific month.",
)
async def get_department_availabilities(
    department_id: str,
    current_user: CurrentUser,  # noqa: ARG001
    service: AvailabilityServiceDep,
    year: int = Query(..., ge=2020, le=2100, description="Year"),
    month: int = Query(..., ge=1, le=12, description="Month (1-12)"),
) -> DepartmentAvailabilityResponse:
    """Get availability for all department members for a month."""
    try:
        return await service.get_department_availabilities(
            department_id=department_id,
            year=year,
            month=month,
        )
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.message,
        ) from e


@router.get(
    "/{department_id}/availabilities/deadline",
    response_model=AvailabilityDeadlineResponse,
    summary="Get availability deadline",
    description="Get the availability submission deadline for a specific month.",
)
async def get_availability_deadline(
    department_id: str,
    current_user: CurrentUser,  # noqa: ARG001
    service: AvailabilityServiceDep,
    year: int = Query(..., ge=2020, le=2100, description="Year"),
    month: int = Query(..., ge=1, le=12, description="Month (1-12)"),
) -> AvailabilityDeadlineResponse:
    """Get the deadline for submitting availability."""
    try:
        return await service.check_deadline(
            department_id=department_id,
            year=year,
            month=month,
        )
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.message,
        ) from e


@router.get(
    "/{department_id}/members/me/availabilities",
    response_model=MemberAvailabilityResponse,
    summary="Get my availabilities",
    description="Get the current user's unavailable dates for a specific month.",
)
async def get_my_availabilities(
    department_id: str,
    current_user: CurrentUser,
    service: AvailabilityServiceDep,
    year: int = Query(..., ge=2020, le=2100, description="Year"),
    month: int = Query(..., ge=1, le=12, description="Month (1-12)"),
) -> MemberAvailabilityResponse:
    """Get the current user's availability for a month."""
    try:
        return await service.get_member_availabilities(
            user_id=current_user.id,
            department_id=department_id,
            year=year,
            month=month,
        )
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.message,
        ) from e


@router.put(
    "/{department_id}/members/me/availabilities",
    response_model=MemberAvailabilityResponse,
    summary="Set my availabilities",
    description="Set the current user's unavailable dates for a specific month. "
    "This replaces all existing entries for the month.",
)
async def set_my_availabilities(
    department_id: str,
    request: SetAvailabilitiesRequest,
    current_user: CurrentUser,
    service: AvailabilityServiceDep,
) -> MemberAvailabilityResponse:
    """
    Set the current user's unavailable dates for a month.

    This operation replaces all existing unavailability entries for the
    specified month with the new dates provided.

    Returns 403 Forbidden if the submission deadline has passed.
    """
    try:
        # Set the availabilities
        await service.set_member_availabilities(
            user_id=current_user.id,
            department_id=department_id,
            year=request.year,
            month=request.month,
            unavailable_dates=request.unavailable_dates,
        )

        # Return the updated availability
        return await service.get_member_availabilities(
            user_id=current_user.id,
            department_id=department_id,
            year=request.year,
            month=request.month,
        )
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.message,
        ) from e
    except ForbiddenError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=e.message,
        ) from e


@router.get(
    "/{department_id}/members/{member_id}/availabilities",
    response_model=MemberAvailabilityResponse,
    summary="Get member availabilities",
    description="Get a specific member's unavailable dates for a month. "
    "Requires department admin/manager role.",
)
async def get_member_availabilities(
    department_id: str,
    member_id: str,
    current_user: CurrentUser,  # noqa: ARG001
    service: AvailabilityServiceDep,
    session: DbSession,
    year: int = Query(..., ge=2020, le=2100, description="Year"),
    month: int = Query(..., ge=1, le=12, description="Month (1-12)"),
) -> MemberAvailabilityResponse:
    """Get a specific member's availability for a month."""
    from app.repositories.member_repository import MemberRepository

    member_repo = MemberRepository(session)

    # Get the member to find their user_id
    member = await member_repo.get_by_id(member_id)
    if not member or member.department_id != department_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Member not found in this department",
        )

    try:
        # Use member's user_id to get their availability
        return await service.get_member_availabilities(
            user_id=member.user_id,
            department_id=department_id,
            year=year,
            month=month,
        )
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.message,
        ) from e
