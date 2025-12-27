"""
User Model.

Represents an authenticated user of the application.
Users belong to an organization and can be members of multiple departments.
"""

import enum
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any
from uuid import uuid4

from sqlalchemy import JSON, Boolean, DateTime, Enum, ForeignKey, Index, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.core.security import get_password_hash, verify_password

if TYPE_CHECKING:
    from app.models.member import Member
    from app.models.organization import Organization
    from app.models.planning import Planning
    from app.models.refresh_token import RefreshToken
    from app.models.service import Service


class UserRole(str, enum.Enum):
    """User role enumeration for authorization."""

    ADMIN = "admin"
    MANAGER = "manager"
    MEMBER = "member"
    GUEST = "guest"


class User(Base):
    """
    User model representing an authenticated user.

    Users are scoped to an organization (multi-tenancy) and can have
    different roles within the platform.

    Attributes:
        id: Unique identifier (UUID)
        organization_id: Foreign key to the organization
        email: User's email address (unique)
        password_hash: Hashed password (nullable for OAuth users)
        first_name: User's first name
        last_name: User's last name
        phone: Optional phone number
        avatar_url: URL to the user's avatar image
        role: User's global role (admin, manager, member, guest)
        email_verified: Whether the email has been verified
        is_active: Whether the account is active
        notification_preferences: JSON object with notification settings
        last_login_at: Timestamp of the last login
        created_at: Timestamp of creation
        updated_at: Timestamp of last update
        deleted_at: Timestamp of soft deletion (null if not deleted)

    Relationships:
        organization: The organization this user belongs to
        refresh_tokens: List of refresh tokens for this user
        members: List of department memberships
        notifications: List of notifications for this user
    """

    __tablename__ = "users"

    # Primary key
    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        default=lambda: str(uuid4()),
        doc="Unique identifier for the user",
    )

    # Foreign key to organization
    organization_id: Mapped[str | None] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=True,
        doc="Foreign key to the user's organization",
    )

    # Authentication fields
    email: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        unique=True,
        doc="User's email address (unique identifier for login)",
    )

    password_hash: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        doc="Hashed password (nullable for OAuth users)",
    )

    # Profile fields
    first_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        doc="User's first name",
    )

    last_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        doc="User's last name",
    )

    phone: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
        default=None,
        doc="User's phone number in E.164 format",
    )

    avatar_url: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
        default=None,
        doc="URL to the user's avatar image",
    )

    # Role and permissions
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole, name="user_role", create_constraint=True),
        nullable=False,
        default=UserRole.MEMBER,
        doc="User's global role for authorization",
    )

    # Status flags
    email_verified: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        doc="Whether the user's email has been verified",
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        doc="Whether the user's account is active",
    )

    # Preferences
    notification_preferences: Mapped[dict[str, Any]] = mapped_column(
        JSON,
        nullable=False,
        default=dict,
        server_default="{}",
        doc="JSON object with notification preferences",
    )

    # Timestamps
    last_login_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        default=None,
        doc="Timestamp of the user's last login",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        doc="Timestamp when the user was created",
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
        doc="Timestamp when the user was last updated",
    )

    # Soft delete support
    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        default=None,
        doc="Timestamp of soft deletion (null if not deleted)",
    )

    # Relationships
    organization: Mapped["Organization | None"] = relationship(
        "Organization",
        back_populates="users",
        lazy="selectin",
    )

    # Note: refresh_tokens relationship will be added when RefreshToken model is created (T0.4.3)
    refresh_tokens: Mapped[list["RefreshToken"]] = relationship(
        "RefreshToken",
        back_populates="user",
        lazy="selectin",
        cascade="all, delete-orphan",
    )

    members: Mapped[list["Member"]] = relationship(
        "Member",
        back_populates="user",
        lazy="selectin",
        cascade="all, delete-orphan",
    )

    created_services: Mapped[list["Service"]] = relationship(
        "Service",
        back_populates="creator",
        lazy="selectin",
    )

    created_plannings: Mapped[list["Planning"]] = relationship(
        "Planning",
        back_populates="creator",
        lazy="selectin",
    )

    # Note: notifications relationship will be added when Notification model is created (T5.1.1)
    # notifications: Mapped[list["Notification"]] = relationship(
    #     "Notification",
    #     back_populates="user",
    #     lazy="selectin",
    #     cascade="all, delete-orphan",
    # )

    # Table indexes
    __table_args__ = (
        Index("ix_users_organization_id", "organization_id"),
        Index("ix_users_is_active", "is_active"),
        Index("ix_users_created_at", "created_at"),
        Index("ix_users_deleted_at", "deleted_at"),
        Index("ix_users_role", "role"),
    )

    def __repr__(self) -> str:
        """String representation for debugging."""
        return f"<User(id={self.id}, email='{self.email}')>"

    def __str__(self) -> str:
        """Human-readable string representation."""
        return f"{self.first_name} {self.last_name}"

    @property
    def full_name(self) -> str:
        """Return the user's full name."""
        return f"{self.first_name} {self.last_name}"

    @property
    def is_deleted(self) -> bool:
        """Check if the user has been soft deleted."""
        return self.deleted_at is not None

    def set_password(self, password: str) -> None:
        """
        Hash and set the user's password.

        Args:
            password: The plain text password to hash.
        """
        self.password_hash = get_password_hash(password)

    def check_password(self, password: str) -> bool:
        """
        Verify a password against the user's stored hash.

        Args:
            password: The plain text password to verify.

        Returns:
            bool: True if the password matches, False otherwise.
        """
        if self.password_hash is None:
            return False
        return verify_password(password, self.password_hash)

    def soft_delete(self) -> None:
        """Mark the user as deleted without removing from database."""
        from datetime import datetime

        self.deleted_at = datetime.now(UTC)
        self.is_active = False

    def restore(self) -> None:
        """Restore a soft-deleted user."""
        self.deleted_at = None
        self.is_active = True
