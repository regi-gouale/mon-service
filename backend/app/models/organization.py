"""
Organization Model.

Represents a church or organization using the SaaS platform.
This is the main tenant entity for multi-tenancy support.
"""

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import uuid4

from sqlalchemy import Boolean, DateTime, Index, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.user import User


class Organization(Base):
    """
    Organization model representing a church or team using the platform.

    This is the primary tenant entity. All other entities (users, departments,
    plannings, etc.) are scoped to an organization for multi-tenancy.

    Attributes:
        id: Unique identifier (UUID)
        name: Display name of the organization
        slug: URL-friendly unique identifier
        description: Optional description of the organization
        logo_url: URL to the organization's logo
        is_active: Whether the organization is active
        created_at: Timestamp of creation
        updated_at: Timestamp of last update

    Relationships:
        users: List of users belonging to this organization
        departments: List of departments in this organization
    """

    __tablename__ = "organizations"

    # Primary key
    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        default=lambda: str(uuid4()),
        doc="Unique identifier for the organization",
    )

    # Required fields
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        doc="Display name of the organization (2-255 characters)",
    )

    slug: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        unique=True,
        index=True,
        doc="URL-friendly unique identifier (lowercase, alphanumeric + hyphens)",
    )

    # Optional fields
    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        default=None,
        doc="Optional description of the organization",
    )

    logo_url: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
        default=None,
        doc="URL to the organization's logo image",
    )

    # Status
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        doc="Whether the organization is currently active",
    )

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        doc="Timestamp when the organization was created",
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
        doc="Timestamp when the organization was last updated",
    )

    # Relationships (lazy loading by default for async compatibility)
    users: Mapped[list["User"]] = relationship(
        "User",
        back_populates="organization",
        lazy="selectin",
        cascade="all, delete-orphan",
    )

    # Note: departments relationship will be added when Department model is created
    # departments: Mapped[list["Department"]] = relationship(
    #     "Department",
    #     back_populates="organization",
    #     lazy="selectin",
    #     cascade="all, delete-orphan",
    # )

    # Table indexes
    __table_args__ = (
        Index("ix_organizations_is_active", "is_active"),
        Index("ix_organizations_created_at", "created_at"),
    )

    def __repr__(self) -> str:
        """String representation for debugging."""
        return f"<Organization(id={self.id}, name='{self.name}', slug='{self.slug}')>"

    def __str__(self) -> str:
        """Human-readable string representation."""
        return self.name
