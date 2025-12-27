"""
Services API Routes.

REST API endpoints for service (event) management.
"""

from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.dependencies import get_current_user, get_db
from app.models.user import User
from app.schemas.planning import (
    ServiceCreate,
    ServiceListResponse,
    ServiceResponse,
    ServiceUpdate,
)
from app.services.service_service import ServiceService

router = APIRouter(prefix="/departments/{department_id}/services", tags=["services"])


def _get_organization_id(user: User) -> str:
    """Get organization ID from user, raise 400 if not set."""
    if not user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User must belong to an organization",
        )
    return user.organization_id


@router.post(
    "",
    response_model=ServiceResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new service",
)
async def create_service(
    department_id: str,
    data: ServiceCreate,
    session: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> ServiceResponse:
    """
    Create a new service for a department.

    Requires admin or manager role in the department.
    """
    service_svc = ServiceService(session)
    org_id = _get_organization_id(current_user)

    service = await service_svc.create_service(
        organization_id=org_id,
        department_id=department_id,
        name=data.name,
        service_type=data.service_type,
        service_date=data.date,
        start_time=data.start_time,
        end_time=data.end_time,
        location=data.location,
        dress_code_id=data.dress_code_id,
        required_roles=[r.model_dump() for r in data.required_roles],
        notes=data.notes,
        is_recurring=data.is_recurring,
        recurrence_rule=data.recurrence_rule,
        created_by=current_user.id,
    )

    return ServiceResponse.model_validate(service)


@router.get(
    "",
    response_model=ServiceListResponse,
    summary="List services for a department",
)
async def list_services(
    department_id: str,
    session: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    year: Annotated[int | None, Query(ge=2020, le=2100)] = None,
    month: Annotated[int | None, Query(ge=1, le=12)] = None,
    start_date: date | None = None,
    end_date: date | None = None,
) -> ServiceListResponse:
    """
    List all services for a department.

    Can filter by year/month or date range.
    """
    service_svc = ServiceService(session)
    org_id = _get_organization_id(current_user)

    services = await service_svc.list_services(
        department_id=department_id,
        organization_id=org_id,
        year=year,
        month=month,
        start_date=start_date,
        end_date=end_date,
    )

    return ServiceListResponse(
        services=[ServiceResponse.model_validate(s) for s in services],
        total=len(services),
    )


@router.get(
    "/{service_id}",
    response_model=ServiceResponse,
    summary="Get a service by ID",
)
async def get_service(
    department_id: str,  # noqa: ARG001
    service_id: str,
    session: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> ServiceResponse:
    """Get a specific service."""
    service_svc = ServiceService(session)
    org_id = _get_organization_id(current_user)

    service = await service_svc.get_service(
        service_id=service_id,
        organization_id=org_id,
    )

    return ServiceResponse.model_validate(service)


@router.patch(
    "/{service_id}",
    response_model=ServiceResponse,
    summary="Update a service",
)
async def update_service(
    department_id: str,  # noqa: ARG001
    service_id: str,
    data: ServiceUpdate,
    session: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> ServiceResponse:
    """Update a service."""
    service_svc = ServiceService(session)
    org_id = _get_organization_id(current_user)

    service = await service_svc.update_service(
        service_id=service_id,
        organization_id=org_id,
        name=data.name,
        service_type=data.service_type,
        service_date=data.date,
        start_time=data.start_time,
        end_time=data.end_time,
        location=data.location,
        dress_code_id=data.dress_code_id,
        required_roles=[r.model_dump() for r in data.required_roles]
        if data.required_roles
        else None,
        notes=data.notes,
        is_recurring=data.is_recurring,
        recurrence_rule=data.recurrence_rule,
    )

    return ServiceResponse.model_validate(service)


@router.delete(
    "/{service_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a service",
)
async def delete_service(
    department_id: str,  # noqa: ARG001
    service_id: str,
    session: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> None:
    """Delete a service."""
    service_svc = ServiceService(session)
    org_id = _get_organization_id(current_user)

    await service_svc.delete_service(
        service_id=service_id,
        organization_id=org_id,
    )
