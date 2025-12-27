"""
Plannings API Routes.

REST API endpoints for planning management.
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.dependencies import get_current_user, get_db
from app.models.planning import PlanningStatus
from app.models.user import User
from app.schemas.planning import (
    AssignmentCreate,
    AssignmentListResponse,
    AssignmentResponse,
    AssignmentStatusUpdate,
    ConflictInfo,
    GenerateRequest,
    GenerationResultResponse,
    PlanningCreate,
    PlanningListResponse,
    PlanningResponse,
    PlanningWithAssignmentsResponse,
)
from app.services.planning_service import PlanningService

router = APIRouter(prefix="/departments/{department_id}/plannings", tags=["plannings"])


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
    response_model=PlanningResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new planning draft",
)
async def create_planning(
    department_id: str,
    data: PlanningCreate,
    session: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> PlanningResponse:
    """
    Create a new planning draft for a month.

    Only one planning per department per month is allowed.
    """
    planning_svc = PlanningService(session)
    org_id = _get_organization_id(current_user)

    planning = await planning_svc.create_planning(
        organization_id=org_id,
        department_id=department_id,
        year=data.year,
        month=data.month,
        created_by=current_user.id,
    )

    return PlanningResponse.model_validate(planning)


@router.get(
    "",
    response_model=PlanningListResponse,
    summary="List plannings for a department",
)
async def list_plannings(
    department_id: str,
    session: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    status_filter: Annotated[
        PlanningStatus | None,
        Query(alias="status", description="Filter by planning status"),
    ] = None,
) -> PlanningListResponse:
    """List all plannings for a department."""
    planning_svc = PlanningService(session)
    org_id = _get_organization_id(current_user)

    plannings = await planning_svc.list_plannings(
        department_id=department_id,
        organization_id=org_id,
        status=status_filter,
    )

    return PlanningListResponse(
        plannings=[PlanningResponse.model_validate(p) for p in plannings],
        total=len(plannings),
    )


@router.get(
    "/{planning_id}",
    response_model=PlanningWithAssignmentsResponse,
    summary="Get a planning with assignments",
)
async def get_planning(
    department_id: str,  # noqa: ARG001
    planning_id: str,
    session: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> PlanningWithAssignmentsResponse:
    """Get a specific planning with all its assignments."""
    planning_svc = PlanningService(session)
    org_id = _get_organization_id(current_user)

    planning = await planning_svc.get_planning(
        planning_id=planning_id,
        organization_id=org_id,
    )

    assignments = await planning_svc.get_assignments_for_planning(
        planning_id=planning_id,
        organization_id=org_id,
    )

    return PlanningWithAssignmentsResponse(
        **PlanningResponse.model_validate(planning).model_dump(),
        assignments=[AssignmentResponse.model_validate(a) for a in assignments],
    )


@router.post(
    "/{planning_id}/generate",
    response_model=GenerationResultResponse,
    summary="Generate planning assignments",
)
async def generate_planning(
    department_id: str,  # noqa: ARG001
    planning_id: str,
    session: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    data: GenerateRequest | None = None,
) -> GenerationResultResponse:
    """
    Generate assignments for a planning using the algorithm.

    Can be called multiple times to regenerate (clears previous assignments).
    """
    planning_svc = PlanningService(session)
    org_id = _get_organization_id(current_user)

    weights = None
    if data and data.weights:
        weights = {
            "equity": data.weights.equity,
            "skills": data.weights.skills,
            "recency": data.weights.recency,
            "random": data.weights.random,
        }

    result = await planning_svc.generate_planning_assignments(
        planning_id=planning_id,
        organization_id=org_id,
        weights=weights,
    )

    return GenerationResultResponse(
        assignments_count=len(result.assignments),
        confidence_score=result.confidence_score,
        conflicts=[ConflictInfo(**c) for c in result.conflicts],
        warnings=result.warnings,
    )


@router.post(
    "/{planning_id}/publish",
    response_model=PlanningResponse,
    summary="Publish a planning",
)
async def publish_planning(
    department_id: str,  # noqa: ARG001
    planning_id: str,
    session: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> PlanningResponse:
    """
    Publish a planning to make it visible to members.

    Planning must be in 'generated' status.
    """
    planning_svc = PlanningService(session)
    org_id = _get_organization_id(current_user)

    planning = await planning_svc.publish_planning(
        planning_id=planning_id,
        organization_id=org_id,
    )

    return PlanningResponse.model_validate(planning)


@router.post(
    "/{planning_id}/archive",
    response_model=PlanningResponse,
    summary="Archive a planning",
)
async def archive_planning(
    department_id: str,  # noqa: ARG001
    planning_id: str,
    session: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> PlanningResponse:
    """Archive a planning."""
    planning_svc = PlanningService(session)
    org_id = _get_organization_id(current_user)

    planning = await planning_svc.archive_planning(
        planning_id=planning_id,
        organization_id=org_id,
    )

    return PlanningResponse.model_validate(planning)


@router.delete(
    "/{planning_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a planning",
)
async def delete_planning(
    department_id: str,  # noqa: ARG001
    planning_id: str,
    session: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> None:
    """
    Delete a planning.

    Only draft plannings can be deleted.
    """
    planning_svc = PlanningService(session)
    org_id = _get_organization_id(current_user)

    await planning_svc.delete_planning(
        planning_id=planning_id,
        organization_id=org_id,
    )


# ============================================================================
# Assignment Routes
# ============================================================================


@router.get(
    "/{planning_id}/assignments",
    response_model=AssignmentListResponse,
    summary="List assignments for a planning",
)
async def list_assignments(
    department_id: str,  # noqa: ARG001
    planning_id: str,
    session: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> AssignmentListResponse:
    """Get all assignments for a planning."""
    planning_svc = PlanningService(session)
    org_id = _get_organization_id(current_user)

    assignments = await planning_svc.get_assignments_for_planning(
        planning_id=planning_id,
        organization_id=org_id,
    )

    return AssignmentListResponse(
        assignments=[AssignmentResponse.model_validate(a) for a in assignments],
        total=len(assignments),
    )


@router.post(
    "/{planning_id}/assignments",
    response_model=AssignmentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add an assignment",
)
async def add_assignment(
    department_id: str,  # noqa: ARG001
    planning_id: str,
    data: AssignmentCreate,
    session: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> AssignmentResponse:
    """Manually add an assignment to a planning."""
    planning_svc = PlanningService(session)
    org_id = _get_organization_id(current_user)

    assignment = await planning_svc.add_assignment(
        planning_id=planning_id,
        organization_id=org_id,
        service_id=data.service_id,
        member_id=data.member_id,
        role=data.assigned_role,
    )

    return AssignmentResponse.model_validate(assignment)


@router.delete(
    "/{planning_id}/assignments/{assignment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remove an assignment",
)
async def remove_assignment(
    department_id: str,  # noqa: ARG001
    planning_id: str,  # noqa: ARG001
    assignment_id: str,
    session: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> None:
    """Remove an assignment from a planning."""
    planning_svc = PlanningService(session)
    org_id = _get_organization_id(current_user)

    await planning_svc.remove_assignment(
        assignment_id=assignment_id,
        organization_id=org_id,
    )


@router.patch(
    "/{planning_id}/assignments/{assignment_id}",
    response_model=AssignmentResponse,
    summary="Update assignment status",
)
async def update_assignment_status(
    department_id: str,
    planning_id: str,  # noqa: ARG001
    assignment_id: str,
    data: AssignmentStatusUpdate,
    session: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> AssignmentResponse:
    """
    Update an assignment status (confirm or decline).

    Members can only update their own assignments.
    """
    planning_svc = PlanningService(session)

    # Get member ID for current user
    from app.repositories.member_repository import MemberRepository

    member_repo = MemberRepository(session)
    member = await member_repo.get_by_user_and_department(
        current_user.id, department_id
    )

    if not member:
        from app.core.exceptions import PermissionDeniedError

        raise PermissionDeniedError("You are not a member of this department")

    org_id = _get_organization_id(current_user)

    if data.action == "confirm":
        assignment = await planning_svc.confirm_assignment(
            assignment_id=assignment_id,
            member_id=member.id,
            organization_id=org_id,
        )
    else:
        assignment = await planning_svc.decline_assignment(
            assignment_id=assignment_id,
            member_id=member.id,
            organization_id=org_id,
        )

    return AssignmentResponse.model_validate(assignment)
