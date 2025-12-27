"""
Availability Model.

Represents unavailability periods for members.
Members can mark specific dates when they are not available for services.
"""

from datetime import date, datetime, time
from typing import TYPE_CHECKING
from uuid import uuid4

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    Index,
    String,
    Time,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.member import Member
    from app.models.organization import Organization


class Availability(Base):
    """
    Availability model representing unavailability periods for members.

    Members use this to mark dates when they are not available for services.
    The planning generator uses this information to avoid assigning members
    on dates they marked as unavailable.

    Attributes:
        id: Unique identifier (UUID)
        organization_id: Foreign key to the organization (tenant key)
        member_id: Foreign key to the member
        date: Date of unavailability
        reason: Optional reason for unavailability
        is_all_day: Whether the unavailability is for the entire day
        start_time: Start time if partial day (required if is_all_day=False)
        end_time: End time if partial day (required if is_all_day=False)
        created_at: Timestamp of creation
        updated_at: Timestamp of last update

    Relationships:
        organization: The organization this availability belongs to
        member: The member this availability is for
    """

    __tablename__ = "availabilities"
    __table_args__ = (
        UniqueConstraint("member_id", "date", name="uq_availabilities_member_date"),
        Index("ix_availabilities_organization_id", "organization_id"),
        Index("ix_availabilities_member_id", "member_id"),
        Index("ix_availabilities_member_date", "member_id", "date"),
    )

    # Primary key
    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        default=lambda: str(uuid4()),
        doc="Unique identifier for the availability entry",
    )

    # Foreign key to organization (tenant key)
    organization_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        doc="Foreign key to the organization (tenant isolation)",
    )

    # Foreign key to member
    member_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("members.id", ondelete="CASCADE"),
        nullable=False,
        doc="Foreign key to the member",
    )

    # Date of unavailability
    date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        doc="Date of unavailability",
    )

    # Optional reason
    reason: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        default=None,
        doc="Optional reason for unavailability",
    )

    # All day flag
    is_all_day: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        doc="Whether the unavailability is for the entire day",
    )

    # Partial day time range
    start_time: Mapped[time | None] = mapped_column(
        Time,
        nullable=True,
        default=None,
        doc="Start time if partial day (required if is_all_day=False)",
    )

    end_time: Mapped[time | None] = mapped_column(
        Time,
        nullable=True,
        default=None,
        doc="End time if partial day (required if is_all_day=False)",
    )

    # Audit fields
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        doc="Timestamp of availability entry creation",
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
        lazy="selectin",
    )

    member: Mapped["Member"] = relationship(
        "Member",
        back_populates="availabilities",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        """Return string representation of the availability."""
        return (
            f"<Availability(id={self.id}, member={self.member_id}, date={self.date})>"
        )
