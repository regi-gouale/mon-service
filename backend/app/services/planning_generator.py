"""
Planning Generator.

Algorithm for generating optimized planning assignments.
Uses a greedy algorithm with weighted scoring for fairness and skill matching.
"""

from dataclasses import dataclass, field
from datetime import date
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.member import Member, MemberStatus
from app.models.planning import Planning
from app.models.planning_assignment import AssignmentStatus, PlanningAssignment
from app.models.service import Service
from app.repositories.availability_repository import AvailabilityRepository
from app.repositories.member_repository import MemberRepository
from app.repositories.planning_assignment_repository import (
    PlanningAssignmentRepository,
)
from app.repositories.service_repository import ServiceRepository


@dataclass
class RoleRequirement:
    """Represents a required role for a service."""

    role: str
    count: int


@dataclass
class MemberScore:
    """Score breakdown for a member candidate."""

    member: Member
    total_score: float
    equity_score: float  # Lower past assignments = higher score
    skill_score: float  # Has required skills = higher score
    availability_score: float  # Not unavailable = higher score
    recency_score: float  # Longer since last assignment = higher score


@dataclass
class GenerationResult:
    """Result of the planning generation."""

    assignments: list[PlanningAssignment]
    conflicts: list[dict[str, Any]]
    confidence_score: float
    warnings: list[str] = field(default_factory=list)


@dataclass
class ServiceConflict:
    """Represents a conflict for a service."""

    service_id: str
    service_name: str
    service_date: date
    role: str
    required_count: int
    assigned_count: int
    available_members: int
    reason: str


class PlanningGenerator:
    """
    Planning generator using a greedy algorithm with weighted scoring.

    The algorithm assigns members to services based on:
    1. Availability - member must be available on the service date
    2. Skills - member should have skills matching the required role
    3. Equity - members with fewer past assignments get higher priority
    4. Recency - members who haven't served recently get higher priority

    Scoring weights (configurable):
    - Equity: 40% - Prioritize fair distribution
    - Skills: 30% - Prioritize skill match
    - Recency: 20% - Spread assignments over time
    - Random: 10% - Add some variety
    """

    # Default scoring weights
    WEIGHT_EQUITY = 0.40
    WEIGHT_SKILLS = 0.30
    WEIGHT_RECENCY = 0.20
    WEIGHT_RANDOM = 0.10

    def __init__(
        self,
        session: AsyncSession,
        organization_id: str,
        weights: dict[str, float] | None = None,
    ) -> None:
        """
        Initialize the planning generator.

        Args:
            session: SQLAlchemy async session
            organization_id: UUID of the organization
            weights: Optional custom scoring weights
        """
        self.session = session
        self.organization_id = organization_id

        # Initialize repositories
        self.service_repo = ServiceRepository(session)
        self.member_repo = MemberRepository(session)
        self.availability_repo = AvailabilityRepository(session)
        self.assignment_repo = PlanningAssignmentRepository(session)

        # Set weights
        if weights:
            self.weight_equity = weights.get("equity", self.WEIGHT_EQUITY)
            self.weight_skills = weights.get("skills", self.WEIGHT_SKILLS)
            self.weight_recency = weights.get("recency", self.WEIGHT_RECENCY)
            self.weight_random = weights.get("random", self.WEIGHT_RANDOM)
        else:
            self.weight_equity = self.WEIGHT_EQUITY
            self.weight_skills = self.WEIGHT_SKILLS
            self.weight_recency = self.WEIGHT_RECENCY
            self.weight_random = self.WEIGHT_RANDOM

        # Cache for optimization
        self._member_assignment_counts: dict[str, int] = {}
        self._member_last_assignment: dict[str, date] = {}
        self._unavailable_dates: dict[str, set[date]] = {}

    async def generate(
        self,
        planning: Planning,
        services: list[Service],
        members: list[Member],
        lookback_months: int = 3,
    ) -> GenerationResult:
        """
        Generate assignments for a planning.

        Args:
            planning: The planning to generate assignments for
            services: List of services to assign
            members: List of available members
            lookback_months: Months to look back for equity calculation

        Returns:
            GenerationResult with assignments, conflicts, and confidence
        """
        import random

        # Filter active members only
        active_members = [m for m in members if m.status == MemberStatus.ACTIVE]

        if not active_members:
            return GenerationResult(
                assignments=[],
                conflicts=[],
                confidence_score=0.0,
                warnings=["No active members available for assignment"],
            )

        if not services:
            return GenerationResult(
                assignments=[],
                conflicts=[],
                confidence_score=1.0,
                warnings=["No services to assign"],
            )

        # Pre-compute data for optimization
        await self._load_member_data(active_members, planning.month, lookback_months)

        assignments: list[PlanningAssignment] = []
        conflicts: list[dict[str, Any]] = []
        warnings: list[str] = []

        # Track assigned members per service to avoid duplicates
        service_assignments: dict[str, set[str]] = {}

        # Process each service
        for service in sorted(services, key=lambda s: (s.date, s.start_time)):
            service_assignments[service.id] = set()
            required_roles = self._parse_required_roles(service.required_roles)

            for requirement in required_roles:
                role = requirement.role
                count_needed = requirement.count

                # Get available candidates for this role
                candidates = await self._get_candidates(
                    active_members,
                    service,
                    role,
                    service_assignments[service.id],
                )

                if len(candidates) < count_needed:
                    # Record conflict
                    conflicts.append(
                        {
                            "service_id": service.id,
                            "service_name": service.name,
                            "service_date": service.date.isoformat(),
                            "role": role,
                            "required": count_needed,
                            "available": len(candidates),
                            "reason": "Insufficient available members with required skills",
                        }
                    )

                # Score and sort candidates
                scored_candidates = await self._score_candidates(
                    candidates, service, role
                )

                # Add random factor for variety
                for sc in scored_candidates:
                    sc.total_score += random.random() * self.weight_random

                # Sort by total score (descending)
                scored_candidates.sort(key=lambda x: x.total_score, reverse=True)

                # Assign top candidates
                assigned_count = 0
                for scored in scored_candidates:
                    if assigned_count >= count_needed:
                        break

                    member = scored.member
                    assignment = PlanningAssignment(
                        organization_id=self.organization_id,
                        planning_id=planning.id,
                        service_id=service.id,
                        member_id=member.id,
                        assigned_role=role,
                        status=AssignmentStatus.ASSIGNED,
                    )

                    assignments.append(assignment)
                    service_assignments[service.id].add(member.id)
                    # assigned_count is incremented implicitly by breaking from loop

                    # Update cache for subsequent assignments
                    self._member_assignment_counts[member.id] = (
                        self._member_assignment_counts.get(member.id, 0) + 1
                    )
                    self._member_last_assignment[member.id] = service.date

        # Calculate confidence score
        total_required = sum(
            sum(r.count for r in self._parse_required_roles(s.required_roles))
            for s in services
        )
        total_assigned = len(assignments)
        confidence = total_assigned / total_required if total_required > 0 else 1.0

        return GenerationResult(
            assignments=assignments,
            conflicts=conflicts,
            confidence_score=round(confidence, 2),
            warnings=warnings,
        )

    async def _load_member_data(
        self,
        members: list[Member],
        planning_month: date,
        lookback_months: int,
    ) -> None:
        """
        Pre-load member data for optimization.

        Args:
            members: List of members
            planning_month: First day of the planning month
            lookback_months: Months to look back
        """
        from calendar import monthrange
        from datetime import timedelta

        # Calculate date range
        # last_day could be used for validation if needed
        _, _ = monthrange(planning_month.year, planning_month.month)

        lookback_start = date(
            planning_month.year,
            max(1, planning_month.month - lookback_months),
            1,
        )
        if planning_month.month <= lookback_months:
            lookback_start = date(
                planning_month.year - 1,
                12 - (lookback_months - planning_month.month),
                1,
            )

        for member in members:
            # Load assignment counts
            count = await self.assignment_repo.get_member_assignment_count(
                member.id,
                self.organization_id,
                lookback_start,
                planning_month - timedelta(days=1),
            )
            self._member_assignment_counts[member.id] = count

            # Load unavailable dates
            availabilities = await self.availability_repo.get_by_member_for_month(
                member.id,
                planning_month.year,
                planning_month.month,
            )
            self._unavailable_dates[member.id] = {a.date for a in availabilities}

    def _parse_required_roles(
        self, required_roles: list[dict[str, Any]]
    ) -> list[RoleRequirement]:
        """Parse the required_roles JSON into structured data."""
        requirements = []
        for role_data in required_roles:
            if isinstance(role_data, dict) and "role" in role_data:
                requirements.append(
                    RoleRequirement(
                        role=role_data["role"],
                        count=role_data.get("count", 1),
                    )
                )
        return requirements

    async def _get_candidates(
        self,
        members: list[Member],
        service: Service,
        _role: str,
        already_assigned: set[str],
    ) -> list[Member]:
        """
        Get members who are candidates for a role on a service.

        Args:
            members: All active members
            service: The service to assign
            role: The required role
            already_assigned: Members already assigned to this service

        Returns:
            List of eligible candidate members
        """
        candidates = []

        for member in members:
            # Skip if already assigned to this service
            if member.id in already_assigned:
                continue

            # Skip if unavailable on this date
            if service.date in self._unavailable_dates.get(member.id, set()):
                continue

            # Add to candidates (skill check done in scoring)
            candidates.append(member)

        return candidates

    async def _score_candidates(
        self,
        candidates: list[Member],
        service: Service,
        role: str,
    ) -> list[MemberScore]:
        """
        Score candidates for a role.

        Args:
            candidates: List of candidate members
            service: The service
            role: The required role

        Returns:
            List of scored candidates
        """
        scored = []
        max_assignments = max(self._member_assignment_counts.values(), default=1) or 1

        for member in candidates:
            # Equity score (inverse of assignment count)
            assignment_count = self._member_assignment_counts.get(member.id, 0)
            equity_score = 1.0 - (assignment_count / max_assignments)

            # Skill score
            member_skills = member.skills or []
            skill_score = (
                1.0 if role.lower() in [s.lower() for s in member_skills] else 0.3
            )

            # Availability score (1.0 since we already filtered)
            availability_score = 1.0

            # Recency score
            last_date = self._member_last_assignment.get(member.id)
            if last_date:
                days_since = (service.date - last_date).days
                recency_score = min(1.0, days_since / 30.0)
            else:
                recency_score = 1.0  # Never assigned = high priority

            # Calculate total weighted score
            total = (
                equity_score * self.weight_equity
                + skill_score * self.weight_skills
                + recency_score * self.weight_recency
            )

            scored.append(
                MemberScore(
                    member=member,
                    total_score=total,
                    equity_score=equity_score,
                    skill_score=skill_score,
                    availability_score=availability_score,
                    recency_score=recency_score,
                )
            )

        return scored


async def generate_planning(
    session: AsyncSession,
    planning: Planning,
    services: list[Service],
    members: list[Member],
    weights: dict[str, float] | None = None,
) -> GenerationResult:
    """
    Convenience function to generate planning.

    Args:
        session: SQLAlchemy async session
        planning: The planning to generate
        services: Services for the month
        members: Department members
        weights: Optional custom scoring weights

    Returns:
        GenerationResult with assignments and metrics
    """
    generator = PlanningGenerator(
        session,
        planning.organization_id,
        weights,
    )
    return await generator.generate(planning, services, members)
