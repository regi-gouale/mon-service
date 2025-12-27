"""
Service Model.

Represents a service/event that requires team members.
Services can be recurring (using RRULE) or one-time events.
"""

from datetime import date, datetime, time
from typing import TYPE_CHECKING, Any
from uuid import uuid4

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    Index,
    String,
    Text,
    Time,
    func,
)
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.department import Department
    from app.models.organization import Organization
    from app.models.planning_assignment import PlanningAssignment
    from app.models.user import User


class Service(Base):
    """
    Service model representing a worship service or event.

    Services are events that require team members to be assigned.
    They can be one-time or recurring (using iCal RRULE format).

    Attributes:
        id: Unique identifier (UUID)
        organization_id: Foreign key to organization (tenant key)
        department_id: Foreign key to department
        name: Display name of the service
        service_type: Type of service (worship, rehearsal, event)
        date: Date of the service
        start_time: Start time
        end_time: Optional end time
        location: Optional location
        dress_code_id: Optional foreign key to dress code
        required_roles: JSON array of required roles with counts
        notes: Optional notes
        is_recurring: Whether this is a recurring service
        recurrence_rule: iCal RRULE for recurring services
        created_at: Timestamp of creation
        updated_at: Timestamp of last update
        created_by: Foreign key to the user who created this service

    Relationships:
        organization: The organization this service belongs to
        department: The department this service belongs to
        creator: The user who created this service
        assignments: List of planning assignments for this service
    """

    __tablename__ = "services"
    __table_args__ = (
        Index("ix_services_organization_id", "organization_id"),
        Index("ix_services_department_id", "department_id"),
        Index("ix_services_date", "date"),
        Index("ix_services_department_date", "department_id", "date"),
    )

    # Primary key
    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        default=lambda: str(uuid4()),
        doc="Unique identifier for the service",
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

    # Required fields
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        doc="Display name of the service",
    )

    service_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        doc="Type of service (culte, répétition, événement)",
    )

    date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        doc="Date of the service",
    )

    start_time: Mapped[time] = mapped_column(
        Time,
        nullable=False,
        doc="Start time of the service",
    )

    # Optional fields
    end_time: Mapped[time | None] = mapped_column(
        Time,
        nullable=True,
        default=None,
        doc="End time of the service (optional)",
    )

    location: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        default=None,
        doc="Location of the service",
    )

    dress_code_id: Mapped[str | None] = mapped_column(
        UUID(as_uuid=False),
        # ForeignKey will be added when DressCode model is created
        nullable=True,
        default=None,
        doc="Foreign key to the dress code (optional)",
    )

    required_roles: Mapped[list[dict[str, Any]]] = mapped_column(
        JSON,
        nullable=False,
        default=list,
        doc='Required roles with counts (e.g., [{"role": "musicien", "count": 3}])',
    )

    notes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        default=None,
        doc="Optional notes about the service",
    )

    is_recurring: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        doc="Whether this is a recurring service",
    )

    recurrence_rule: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        default=None,
        doc="iCal RRULE for recurring services",
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
        doc="Foreign key to the user who created this service",
    )

    # Relationships
    organization: Mapped["Organization"] = relationship(
        "Organization",
        back_populates="services",
        lazy="selectin",
    )

    department: Mapped["Department"] = relationship(
        "Department",
        back_populates="services",
        lazy="selectin",
    )

    creator: Mapped["User"] = relationship(
        "User",
        back_populates="created_services",
        lazy="selectin",
    )

    assignments: Mapped[list["PlanningAssignment"]] = relationship(
        "PlanningAssignment",
        back_populates="service",
        lazy="selectin",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        """String representation of the service."""
        return f"<Service(id={self.id}, name='{self.name}', date={self.date})>"
