"""
Planning Service.

Business logic for planning management.
"""

from datetime import date, datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import (
    ConflictError,
    NotFoundError,
    PermissionDeniedError,
    ValidationError,
)
from app.models.planning import Planning, PlanningStatus
from app.models.planning_assignment import AssignmentStatus, PlanningAssignment
from app.repositories.department_repository import DepartmentRepository
from app.repositories.member_repository import MemberRepository
from app.repositories.planning_assignment_repository import (
    PlanningAssignmentRepository,
)
from app.repositories.planning_repository import PlanningRepository
from app.repositories.service_repository import ServiceRepository
from app.services.planning_generator import GenerationResult, generate_planning


class PlanningService:
    """Service for planning operations."""

    def __init__(self, session: AsyncSession) -> None:
        """
        Initialize the service.

        Args:
            session: SQLAlchemy async session
        """
        self.session = session
        self.planning_repo = PlanningRepository(session)
        self.service_repo = ServiceRepository(session)
        self.member_repo = MemberRepository(session)
        self.department_repo = DepartmentRepository(session)
        self.assignment_repo = PlanningAssignmentRepository(session)

    async def create_planning(
        self,
        organization_id: str,
        department_id: str,
        year: int,
        month: int,
        created_by: str,
    ) -> Planning:
        """
        Create a new planning draft.

        Args:
            organization_id: UUID of the organization
            department_id: UUID of the department
            year: Year for the planning
            month: Month for the planning (1-12)
            created_by: UUID of the user creating the planning

        Returns:
            Created planning

        Raises:
            ConflictError: If planning already exists for this month
            NotFoundError: If department not found
        """
        # Verify department exists
        department = await self.department_repo.get_by_id(department_id)
        if not department or department.organization_id != organization_id:
            raise NotFoundError("Department", department_id)

        # Check for existing planning
        planning_month = date(year, month, 1)
        existing = await self.planning_repo.get_by_department_and_month(
            department_id, organization_id, planning_month
        )
        if existing:
            raise ConflictError(
                f"Planning already exists for {year}-{month:02d}. "
                f"Delete or archive it first."
            )

        # Create planning
        planning = Planning(
            organization_id=organization_id,
            department_id=department_id,
            month=planning_month,
            status=PlanningStatus.DRAFT,
            created_by=created_by,
        )

        planning = await self.planning_repo.create(planning)
        await self.session.commit()

        return planning

    async def get_planning(
        self,
        planning_id: str,
        organization_id: str,
    ) -> Planning:
        """
        Get a planning by ID.

        Args:
            planning_id: UUID of the planning
            organization_id: UUID of the organization

        Returns:
            Planning entity

        Raises:
            NotFoundError: If planning not found
        """
        planning = await self.planning_repo.get_by_id_and_organization(
            planning_id, organization_id
        )
        if not planning:
            raise NotFoundError("Planning", planning_id)
        return planning

    async def get_planning_for_month(
        self,
        department_id: str,
        organization_id: str,
        year: int,
        month: int,
    ) -> Planning | None:
        """
        Get planning for a specific month.

        Args:
            department_id: UUID of the department
            organization_id: UUID of the organization
            year: Year
            month: Month (1-12)

        Returns:
            Planning or None if not found
        """
        planning_month = date(year, month, 1)
        return await self.planning_repo.get_by_department_and_month(
            department_id, organization_id, planning_month
        )

    async def list_plannings(
        self,
        department_id: str,
        organization_id: str,
        status: PlanningStatus | None = None,
    ) -> list[Planning]:
        """
        List plannings for a department.

        Args:
            department_id: UUID of the department
            organization_id: UUID of the organization
            status: Optional status filter

        Returns:
            List of plannings
        """
        plannings = await self.planning_repo.get_by_department(
            department_id, organization_id, status
        )
        return list(plannings)

    async def generate_planning_assignments(
        self,
        planning_id: str,
        organization_id: str,
        weights: dict[str, float] | None = None,
    ) -> GenerationResult:
        """
        Generate assignments for a planning.

        Args:
            planning_id: UUID of the planning
            organization_id: UUID of the organization
            weights: Optional custom scoring weights

        Returns:
            GenerationResult with assignments and metrics

        Raises:
            NotFoundError: If planning not found
            ValidationError: If planning is not in draft status
        """
        planning = await self.get_planning(planning_id, organization_id)

        if planning.status not in [PlanningStatus.DRAFT, PlanningStatus.GENERATED]:
            raise ValidationError(
                f"Cannot generate assignments for planning in status {planning.status.value}. "
                "Only draft or generated plannings can be regenerated."
            )

        # Get services for this month
        services = await self.service_repo.get_by_month(
            planning.department_id,
            organization_id,
            planning.month.year,
            planning.month.month,
        )

        # Get active members for this department
        members = await self.member_repo.get_active_members_for_department(
            planning.department_id
        )

        # Clear existing assignments if regenerating
        if planning.status == PlanningStatus.GENERATED:
            await self.assignment_repo.delete_by_planning(planning_id, organization_id)

        # Generate assignments
        result = await generate_planning(
            self.session,
            planning,
            list(services),
            list(members),
            weights,
        )

        # Save assignments
        if result.assignments:
            await self.assignment_repo.create_bulk(result.assignments)

        # Update planning status
        planning.status = PlanningStatus.GENERATED
        planning.confidence_score = result.confidence_score
        planning.generated_at = datetime.now()
        await self.planning_repo.update(planning)
        await self.session.commit()

        return result

    async def publish_planning(
        self,
        planning_id: str,
        organization_id: str,
    ) -> Planning:
        """
        Publish a planning to make it visible to members.

        Args:
            planning_id: UUID of the planning
            organization_id: UUID of the organization

        Returns:
            Updated planning

        Raises:
            NotFoundError: If planning not found
            ValidationError: If planning is not generated
        """
        planning = await self.get_planning(planning_id, organization_id)

        if planning.status != PlanningStatus.GENERATED:
            raise ValidationError(
                f"Cannot publish planning in status {planning.status.value}. "
                "Generate assignments first."
            )

        planning.status = PlanningStatus.PUBLISHED
        planning.published_at = datetime.now()
        await self.planning_repo.update(planning)
        await self.session.commit()

        return planning

    async def archive_planning(
        self,
        planning_id: str,
        organization_id: str,
    ) -> Planning:
        """
        Archive a planning.

        Args:
            planning_id: UUID of the planning
            organization_id: UUID of the organization

        Returns:
            Updated planning
        """
        planning = await self.get_planning(planning_id, organization_id)
        planning.status = PlanningStatus.ARCHIVED
        await self.planning_repo.update(planning)
        await self.session.commit()
        return planning

    async def delete_planning(
        self,
        planning_id: str,
        organization_id: str,
    ) -> None:
        """
        Delete a planning.

        Only draft plannings can be deleted.

        Args:
            planning_id: UUID of the planning
            organization_id: UUID of the organization

        Raises:
            NotFoundError: If planning not found
            ValidationError: If planning is not a draft
        """
        planning = await self.get_planning(planning_id, organization_id)

        if planning.status != PlanningStatus.DRAFT:
            raise ValidationError(
                f"Cannot delete planning in status {planning.status.value}. "
                "Only draft plannings can be deleted."
            )

        await self.planning_repo.delete(planning)
        await self.session.commit()

    async def get_assignments_for_planning(
        self,
        planning_id: str,
        organization_id: str,
    ) -> list[PlanningAssignment]:
        """
        Get all assignments for a planning.

        Args:
            planning_id: UUID of the planning
            organization_id: UUID of the organization

        Returns:
            List of assignments
        """
        # Verify planning exists
        await self.get_planning(planning_id, organization_id)

        assignments = await self.assignment_repo.get_by_planning(
            planning_id, organization_id
        )
        return list(assignments)

    async def add_assignment(
        self,
        planning_id: str,
        organization_id: str,
        service_id: str,
        member_id: str,
        role: str,
    ) -> PlanningAssignment:
        """
        Manually add an assignment to a planning.

        Args:
            planning_id: UUID of the planning
            organization_id: UUID of the organization
            service_id: UUID of the service
            member_id: UUID of the member
            role: Role to assign

        Returns:
            Created assignment

        Raises:
            ConflictError: If assignment already exists
        """
        planning = await self.get_planning(planning_id, organization_id)

        if planning.status == PlanningStatus.ARCHIVED:
            raise ValidationError("Cannot modify archived planning")

        # Check for existing assignment
        existing = await self.assignment_repo.get_by_service_and_member(
            service_id, member_id
        )
        if existing:
            raise ConflictError("Member is already assigned to this service")

        assignment = PlanningAssignment(
            organization_id=organization_id,
            planning_id=planning_id,
            service_id=service_id,
            member_id=member_id,
            assigned_role=role,
            status=AssignmentStatus.ASSIGNED,
        )

        assignment = await self.assignment_repo.create(assignment)
        await self.session.commit()

        return assignment

    async def remove_assignment(
        self,
        assignment_id: str,
        organization_id: str,
    ) -> None:
        """
        Remove an assignment from a planning.

        Args:
            assignment_id: UUID of the assignment
            organization_id: UUID of the organization

        Raises:
            NotFoundError: If assignment not found
        """
        assignment = await self.assignment_repo.get_by_id(assignment_id)
        if not assignment or assignment.organization_id != organization_id:
            raise NotFoundError("Assignment", assignment_id)

        # Check planning status
        planning = await self.get_planning(assignment.planning_id, organization_id)
        if planning.status == PlanningStatus.ARCHIVED:
            raise ValidationError("Cannot modify archived planning")

        await self.assignment_repo.delete(assignment)
        await self.session.commit()

    async def confirm_assignment(
        self,
        assignment_id: str,
        member_id: str,
        organization_id: str,
    ) -> PlanningAssignment:
        """
        Member confirms their assignment.

        Args:
            assignment_id: UUID of the assignment
            member_id: UUID of the member
            organization_id: UUID of the organization

        Returns:
            Updated assignment

        Raises:
            NotFoundError: If assignment not found
            PermissionDeniedError: If member doesn't own this assignment
        """
        assignment = await self.assignment_repo.get_by_id(assignment_id)
        if not assignment or assignment.organization_id != organization_id:
            raise NotFoundError("Assignment", assignment_id)

        if assignment.member_id != member_id:
            raise PermissionDeniedError("Cannot confirm another member's assignment")

        assignment.status = AssignmentStatus.CONFIRMED
        assignment.confirmed_at = datetime.now()
        await self.assignment_repo.update(assignment)
        await self.session.commit()

        return assignment

    async def decline_assignment(
        self,
        assignment_id: str,
        member_id: str,
        organization_id: str,
    ) -> PlanningAssignment:
        """
        Member declines their assignment.

        Args:
            assignment_id: UUID of the assignment
            member_id: UUID of the member
            organization_id: UUID of the organization

        Returns:
            Updated assignment
        """
        assignment = await self.assignment_repo.get_by_id(assignment_id)
        if not assignment or assignment.organization_id != organization_id:
            raise NotFoundError("Assignment", assignment_id)

        if assignment.member_id != member_id:
            raise PermissionDeniedError("Cannot decline another member's assignment")

        assignment.status = AssignmentStatus.DECLINED
        await self.assignment_repo.update(assignment)
        await self.session.commit()

        return assignment

    async def get_member_assignments(
        self,
        member_id: str,
        organization_id: str,
        status: AssignmentStatus | None = None,
    ) -> list[PlanningAssignment]:
        """
        Get assignments for a member.

        Args:
            member_id: UUID of the member
            organization_id: UUID of the organization
            status: Optional status filter

        Returns:
            List of assignments
        """
        assignments = await self.assignment_repo.get_by_member(
            member_id, organization_id, status
        )
        return list(assignments)
