"""
PlanningAssignment Model.

Represents the assignment of a member to a service within a planning.
"""

import enum
from datetime import datetime
from typing import TYPE_CHECKING
from uuid import uuid4

from sqlalchemy import (
    DateTime,
    Enum,
    ForeignKey,
    Index,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.member import Member
    from app.models.organization import Organization
    from app.models.planning import Planning
    from app.models.service import Service


class AssignmentStatus(str, enum.Enum):
    """Assignment status enumeration."""

    ASSIGNED = "assigned"
    CONFIRMED = "confirmed"
    DECLINED = "declined"
    REPLACED = "replaced"


class PlanningAssignment(Base):
    """
    PlanningAssignment model representing a member's assignment to a service.

    Each assignment connects a member to a service within a planning,
    with a specific role and status.

    Attributes:
        id: Unique identifier (UUID)
        organization_id: Foreign key to organization (tenant key)
        planning_id: Foreign key to the planning
        service_id: Foreign key to the service
        member_id: Foreign key to the member
        assigned_role: The role assigned to this member for this service
        status: Current status of the assignment
        confirmed_at: When the member confirmed their assignment
        notes: Optional notes about the assignment
        created_at: Timestamp of creation
        updated_at: Timestamp of last update

    Relationships:
        organization: The organization this assignment belongs to
        planning: The planning this assignment is part of
        service: The service the member is assigned to
        member: The member who is assigned
    """

    __tablename__ = "planning_assignments"
    __table_args__ = (
        UniqueConstraint(
            "service_id", "member_id", name="uq_assignments_service_member"
        ),
        Index("ix_planning_assignments_organization_id", "organization_id"),
        Index("ix_planning_assignments_planning_id", "planning_id"),
        Index("ix_planning_assignments_service_id", "service_id"),
        Index("ix_planning_assignments_member_id", "member_id"),
    )

    # Primary key
    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        default=lambda: str(uuid4()),
        doc="Unique identifier for the assignment",
    )

    # Foreign key to organization (tenant key)
    organization_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        doc="Foreign key to the organization (tenant isolation)",
    )

    # Foreign key to planning
    planning_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("plannings.id", ondelete="CASCADE"),
        nullable=False,
        doc="Foreign key to the planning",
    )

    # Foreign key to service
    service_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("services.id", ondelete="CASCADE"),
        nullable=False,
        doc="Foreign key to the service",
    )

    # Foreign key to member
    member_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("members.id", ondelete="CASCADE"),
        nullable=False,
        doc="Foreign key to the assigned member",
    )

    # Assignment details
    assigned_role: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        doc="The role assigned to this member for this service",
    )

    status: Mapped[AssignmentStatus] = mapped_column(
        Enum(AssignmentStatus, name="assignment_status"),
        nullable=False,
        default=AssignmentStatus.ASSIGNED,
        doc="Current status of the assignment",
    )

    confirmed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        default=None,
        doc="When the member confirmed their assignment",
    )

    notes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        default=None,
        doc="Optional notes about the assignment",
    )

    # Audit fields
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        doc="Timestamp of creation",
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
        doc="Timestamp of last update",
    )

    # Relationships
    organization: Mapped["Organization"] = relationship(
        "Organization",
        back_populates="planning_assignments",
        lazy="selectin",
    )

    planning: Mapped["Planning"] = relationship(
        "Planning",
        back_populates="assignments",
        lazy="selectin",
    )

    service: Mapped["Service"] = relationship(
        "Service",
        back_populates="assignments",
        lazy="selectin",
    )

    member: Mapped["Member"] = relationship(
        "Member",
        back_populates="assignments",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        """String representation of the assignment."""
        return (
            f"<PlanningAssignment(id={self.id}, "
            f"member_id={self.member_id}, "
            f"role='{self.assigned_role}', "
            f"status={self.status.value})>"
        )
