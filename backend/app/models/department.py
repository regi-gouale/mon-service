"""
Department Model.

Represents a department/team within an organization.
Departments contain members who can be assigned to services and plannings.
"""

from datetime import datetime
from typing import TYPE_CHECKING, Any
from uuid import uuid4

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.member import Member
    from app.models.organization import Organization
    from app.models.planning import Planning
    from app.models.service import Service
    from app.models.user import User


class Department(Base):
    """
    Department model representing a team within an organization.

    Departments are used to organize members into groups with specific
    purposes (e.g., worship team, tech team, welcome team).

    Attributes:
        id: Unique identifier (UUID)
        organization_id: Foreign key to the organization
        name: Display name of the department
        description: Optional description
        settings: JSON object with department-specific settings
        availability_deadline_days: Days before deadline for availability submission
        is_active: Whether the department is active
        created_at: Timestamp of creation
        updated_at: Timestamp of last update
        created_by: Foreign key to the user who created this department

    Relationships:
        organization: The organization this department belongs to
        creator: The user who created this department
        members: List of members in this department
        services: List of services for this department
        plannings: List of plannings for this department
    """

    __tablename__ = "departments"
    __table_args__ = (
        UniqueConstraint("organization_id", "name", name="uq_departments_org_name"),
        Index("ix_departments_organization_id", "organization_id"),
    )

    # Primary key
    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        default=lambda: str(uuid4()),
        doc="Unique identifier for the department",
    )

    # Foreign key to organization
    organization_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        doc="Foreign key to the department's organization",
    )

    # Required fields
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        doc="Display name of the department (2-255 characters)",
    )

    # Optional fields
    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        default=None,
        doc="Optional description of the department",
    )

    settings: Mapped[dict[str, Any]] = mapped_column(
        JSON,
        nullable=False,
        default=dict,
        doc="Department-specific settings (JSON)",
    )

    availability_deadline_days: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=7,
        doc="Number of days before the month for availability submission deadline (1-30)",
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        doc="Whether the department is active",
    )

    # Audit fields
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        doc="Timestamp of department creation",
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
        nullable=True,
        doc="Foreign key to the user who created this department",
    )

    # Relationships
    organization: Mapped["Organization"] = relationship(
        "Organization",
        back_populates="departments",
        lazy="selectin",
    )

    creator: Mapped["User | None"] = relationship(
        "User",
        foreign_keys=[created_by],
        lazy="selectin",
    )

    members: Mapped[list["Member"]] = relationship(
        "Member",
        back_populates="department",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    services: Mapped[list["Service"]] = relationship(
        "Service",
        back_populates="department",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    plannings: Mapped[list["Planning"]] = relationship(
        "Planning",
        back_populates="department",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        """Return string representation of the department."""
        return (
            f"<Department(id={self.id}, name={self.name}, org={self.organization_id})>"
        )
