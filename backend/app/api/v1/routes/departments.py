"""
Department API Routes.

REST endpoints for department management.
"""

from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.dependencies import get_current_user
from app.core.database import get_db
from app.core.exceptions import AlreadyExistsError, NotFoundError
from app.core.logging import get_logger
from app.models.user import User
from app.repositories.department_repository import DepartmentRepository

logger = get_logger(__name__)

router = APIRouter(prefix="/departments", tags=["Departments"])

# Type aliases
DbSession = Annotated[AsyncSession, Depends(get_db)]
CurrentUser = Annotated[User, Depends(get_current_user)]


# Schemas
class DepartmentCreateRequest(BaseModel):
    """Schema for creating a department."""

    model_config = ConfigDict(populate_by_name=True)

    name: str = Field(..., min_length=2, max_length=255, description="Department name")
    description: str | None = Field(None, description="Optional description")
    availability_deadline_days: Annotated[
        int, Field(alias="availabilityDeadlineDays")
    ] = Field(
        7, ge=1, le=30, description="Days before deadline for availability submission"
    )
    settings: dict[str, Any] | None = Field(None, description="Department settings")


class DepartmentUpdateRequest(BaseModel):
    """Schema for updating a department."""

    model_config = ConfigDict(populate_by_name=True)

    name: str | None = Field(
        None, min_length=2, max_length=255, description="Department name"
    )
    description: str | None = Field(None, description="Optional description")
    availability_deadline_days: Annotated[
        int | None, Field(alias="availabilityDeadlineDays")
    ] = Field(None, ge=1, le=30, description="Days before deadline")
    settings: dict[str, Any] | None = Field(None, description="Department settings")
    is_active: Annotated[bool | None, Field(alias="isActive")] = Field(
        None, description="Whether the department is active"
    )


class DepartmentResponse(BaseModel):
    """Schema for department response."""

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: str = Field(..., description="Department ID")
    organization_id: Annotated[str, Field(alias="organizationId")] = Field(
        ..., description="Organization ID"
    )
    name: str = Field(..., description="Department name")
    description: str | None = Field(None, description="Description")
    availability_deadline_days: Annotated[
        int, Field(alias="availabilityDeadlineDays")
    ] = Field(..., description="Days before deadline")
    is_active: Annotated[bool, Field(alias="isActive")] = Field(
        ..., description="Whether active"
    )


def get_department_repo(session: DbSession) -> DepartmentRepository:
    """Get department repository instance."""
    return DepartmentRepository(session)


DepartmentRepoDep = Annotated[DepartmentRepository, Depends(get_department_repo)]


@router.post(
    "",
    response_model=DepartmentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a department",
    description="Create a new department in the user's organization.",
)
async def create_department(
    request: DepartmentCreateRequest,
    current_user: CurrentUser,
    repo: DepartmentRepoDep,
) -> DepartmentResponse:
    """Create a new department."""
    if not current_user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User must belong to an organization",
        )

    try:
        department = await repo.create(
            organization_id=current_user.organization_id,
            name=request.name,
            description=request.description,
            settings=request.settings or {},
            availability_deadline_days=request.availability_deadline_days,
            created_by=current_user.id,
        )
        return DepartmentResponse.model_validate(department)
    except AlreadyExistsError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=e.message,
        ) from e


@router.get(
    "",
    response_model=list[DepartmentResponse],
    summary="List departments",
    description="List all departments in the user's organization.",
)
async def list_departments(
    current_user: CurrentUser,
    repo: DepartmentRepoDep,
    include_inactive: bool = Query(False, alias="includeInactive"),
) -> list[DepartmentResponse]:
    """List all departments."""
    if not current_user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User must belong to an organization",
        )

    departments = await repo.get_by_organization(
        organization_id=current_user.organization_id,
        include_inactive=include_inactive,
    )
    return [DepartmentResponse.model_validate(d) for d in departments]


@router.get(
    "/{department_id}",
    response_model=DepartmentResponse,
    summary="Get department",
    description="Get a department by ID.",
)
async def get_department(
    department_id: str,
    current_user: CurrentUser,
    repo: DepartmentRepoDep,
) -> DepartmentResponse:
    """Get a department by ID."""
    try:
        department = await repo.get_by_id_or_raise(
            department_id=department_id,
            organization_id=current_user.organization_id,
        )
        return DepartmentResponse.model_validate(department)
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.message,
        ) from e


@router.patch(
    "/{department_id}",
    response_model=DepartmentResponse,
    summary="Update department",
    description="Update a department.",
)
async def update_department(
    department_id: str,
    request: DepartmentUpdateRequest,
    current_user: CurrentUser,
    repo: DepartmentRepoDep,
) -> DepartmentResponse:
    """Update a department."""
    if not current_user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User must belong to an organization",
        )

    update_data = request.model_dump(exclude_unset=True, by_alias=False)

    try:
        department = await repo.update(
            department_id=department_id,
            organization_id=current_user.organization_id,
            **update_data,
        )
        return DepartmentResponse.model_validate(department)
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.message,
        ) from e
    except AlreadyExistsError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=e.message,
        ) from e


@router.delete(
    "/{department_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete department",
    description="Delete a department.",
)
async def delete_department(
    department_id: str,
    current_user: CurrentUser,
    repo: DepartmentRepoDep,
) -> None:
    """Delete a department."""
    if not current_user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User must belong to an organization",
        )

    deleted = await repo.delete(
        department_id=department_id,
        organization_id=current_user.organization_id,
    )

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Department not found",
        )
