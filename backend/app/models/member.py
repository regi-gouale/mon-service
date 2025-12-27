"""
Member Model.

Represents the membership of a user in a department.
A user can be a member of multiple departments with different roles.
"""

import enum
from datetime import datetime
from typing import TYPE_CHECKING
from uuid import uuid4

from sqlalchemy import (
    JSON,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.availability import Availability
    from app.models.department import Department
    from app.models.organization import Organization
    from app.models.planning_assignment import PlanningAssignment
    from app.models.user import User


class MemberRole(str, enum.Enum):
    """Member role enumeration within a department."""

    ADMIN = "admin"
    MANAGER = "manager"
    MEMBER = "member"


class MemberStatus(str, enum.Enum):
    """Member status enumeration."""

    PENDING = "pending"
    ACTIVE = "active"
    INACTIVE = "inactive"


class Member(Base):
    """
    Member model representing a user's membership in a department.

    A user can belong to multiple departments with different roles.
    This is the join table between User and Department with additional
    membership-specific attributes.

    Attributes:
        id: Unique identifier (UUID)
        organization_id: Foreign key to the organization (tenant key)
        department_id: Foreign key to the department
        user_id: Foreign key to the user
        role: Role within the department (admin, manager, member)
        skills: Array of skills/competencies
        status: Membership status (pending, active, inactive)
        joined_at: Timestamp when the user joined the department
        created_at: Timestamp of creation
        updated_at: Timestamp of last update

    Relationships:
        organization: The organization this membership belongs to
        department: The department the user is a member of
        user: The user who is a member
        availabilities: List of availability entries for this member
    """

    __tablename__ = "members"
    __table_args__ = (
        UniqueConstraint("department_id", "user_id", name="uq_members_dept_user"),
        Index("ix_members_organization_id", "organization_id"),
        Index("ix_members_department_id", "department_id"),
        Index("ix_members_user_id", "user_id"),
    )

    # Primary key
    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        default=lambda: str(uuid4()),
        doc="Unique identifier for the membership",
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

    # Foreign key to user
    user_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        doc="Foreign key to the user",
    )

    # Role within the department
    role: Mapped[MemberRole] = mapped_column(
        Enum(MemberRole, name="member_role"),
        nullable=False,
        default=MemberRole.MEMBER,
        doc="Role within the department (admin, manager, member)",
    )

    # Skills array (stored as JSON for SQLite compatibility)
    skills: Mapped[list[str]] = mapped_column(
        JSON,
        nullable=False,
        default=list,
        doc="Array of skills/competencies (max 20)",
    )

    # Status
    status: Mapped[MemberStatus] = mapped_column(
        Enum(MemberStatus, name="member_status"),
        nullable=False,
        default=MemberStatus.ACTIVE,
        doc="Membership status (pending, active, inactive)",
    )

    # Joined timestamp
    joined_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        doc="Timestamp when the user joined the department",
    )

    # Audit fields
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        doc="Timestamp of membership creation",
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

    department: Mapped["Department"] = relationship(
        "Department",
        back_populates="members",
        lazy="selectin",
    )

    user: Mapped["User"] = relationship(
        "User",
        back_populates="members",
        lazy="selectin",
    )

    availabilities: Mapped[list["Availability"]] = relationship(
        "Availability",
        back_populates="member",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    assignments: Mapped[list["PlanningAssignment"]] = relationship(
        "PlanningAssignment",
        back_populates="member",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        """Return string representation of the membership."""
        return f"<Member(id={self.id}, user={self.user_id}, dept={self.department_id}, role={self.role.value})>"
