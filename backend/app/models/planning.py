"""
Planning Model.

Represents a monthly planning for a department.
Plannings contain assignments of members to services.
"""

import enum
from datetime import date, datetime
from typing import TYPE_CHECKING
from uuid import uuid4

from sqlalchemy import (
    Date,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Index,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.department import Department
    from app.models.organization import Organization
    from app.models.planning_assignment import PlanningAssignment
    from app.models.user import User


class PlanningStatus(str, enum.Enum):
    """Planning status enumeration."""

    DRAFT = "draft"
    GENERATED = "generated"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class Planning(Base):
    """
    Planning model representing a monthly schedule for a department.

    A planning groups all service assignments for a given month.
    It goes through several states: draft -> generated -> published -> archived.

    Attributes:
        id: Unique identifier (UUID)
        organization_id: Foreign key to organization (tenant key)
        department_id: Foreign key to department
        month: First day of the month this planning covers
        status: Current status of the planning
        confidence_score: Algorithm confidence score (0-1)
        generated_at: When the planning was auto-generated
        published_at: When the planning was published
        created_at: Timestamp of creation
        updated_at: Timestamp of last update
        created_by: Foreign key to the user who created this planning

    Relationships:
        organization: The organization this planning belongs to
        department: The department this planning is for
        creator: The user who created this planning
        assignments: List of assignments in this planning
    """

    __tablename__ = "plannings"
    __table_args__ = (
        UniqueConstraint("department_id", "month", name="uq_plannings_dept_month"),
        Index("ix_plannings_organization_id", "organization_id"),
        Index("ix_plannings_department_id", "department_id"),
    )

    # Primary key
    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        default=lambda: str(uuid4()),
        doc="Unique identifier for the planning",
    )

    # Foreign key to organization (tenant key)
    organization_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        doc="Foreign key to the organization (tenant isolation)",
    )

    # Foreign key to department
    department_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("departments.id", ondelete="CASCADE"),
        nullable=False,
        doc="Foreign key to the department",
    )

    # Planning period (always first day of month)
    month: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        doc="First day of the month this planning covers",
    )

    # Status
    status: Mapped[PlanningStatus] = mapped_column(
        Enum(PlanningStatus, name="planning_status"),
        nullable=False,
        default=PlanningStatus.DRAFT,
        doc="Current status of the planning",
    )

    # Algorithm metrics
    confidence_score: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
        default=None,
        doc="Algorithm confidence score (0-1), null if not yet generated",
    )

    # Timestamps for workflow
    generated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        default=None,
        doc="When the planning was auto-generated",
    )

    published_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        default=None,
        doc="When the planning was published to members",
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

    created_by: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=False,
        doc="Foreign key to the user who created this planning",
    )

    # Relationships
    organization: Mapped["Organization"] = relationship(
        "Organization",
        back_populates="plannings",
        lazy="selectin",
    )

    department: Mapped["Department"] = relationship(
        "Department",
        back_populates="plannings",
        lazy="selectin",
    )

    creator: Mapped["User"] = relationship(
        "User",
        back_populates="created_plannings",
        lazy="selectin",
    )

    assignments: Mapped[list["PlanningAssignment"]] = relationship(
        "PlanningAssignment",
        back_populates="planning",
        lazy="selectin",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        """String representation of the planning."""
        return (
            f"<Planning(id={self.id}, month={self.month}, status={self.status.value})>"
        )
