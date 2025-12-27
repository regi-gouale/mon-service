"""
RefreshToken Model.

Manages refresh tokens for JWT authentication.
Tokens are used to obtain new access tokens without re-authentication.
"""

from datetime import UTC, datetime
from typing import TYPE_CHECKING
from uuid import uuid4

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.user import User


class RefreshToken(Base):
    """
    RefreshToken model for managing JWT refresh tokens.

    Refresh tokens have a longer lifetime than access tokens and are used
    to obtain new access tokens without requiring the user to log in again.

    Attributes:
        id: Unique identifier (UUID)
        user_id: Foreign key to the user
        token: The refresh token string (unique)
        expires_at: When the token expires
        created_at: Timestamp of creation
        is_revoked: Whether the token has been revoked

    Relationships:
        user: The user this token belongs to
    """

    __tablename__ = "refresh_tokens"

    # Primary Key
    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        default=lambda: str(uuid4()),
    )

    # Foreign Key
    user_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )

    # Token Data
    token: Mapped[str] = mapped_column(
        String(512),
        unique=True,
        nullable=False,
    )

    # Expiration
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    # Status
    is_revoked: Mapped[bool] = mapped_column(
        Boolean,
        insert_default=False,
        server_default="false",
        nullable=False,
    )

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # Indexes
    __table_args__ = (
        Index("ix_refresh_tokens_user_id_expires_at", "user_id", "expires_at"),
        Index("ix_refresh_tokens_token", "token"),
    )

    # Relationships
    user: Mapped["User"] = relationship(
        "User",
        back_populates="refresh_tokens",
    )

    def __repr__(self) -> str:
        """Return a string representation of the RefreshToken."""
        return (
            f"<RefreshToken(id={self.id}, user_id={self.user_id}, "
            f"expires_at={self.expires_at}, is_revoked={self.is_revoked})>"
        )

    @property
    def is_expired(self) -> bool:
        """Check if the token has expired."""
        return datetime.now(UTC) > self.expires_at

    @property
    def is_valid(self) -> bool:
        """Check if the token is valid (not expired and not revoked)."""
        return not self.is_expired and not self.is_revoked

    def revoke(self) -> None:
        """Revoke the token."""
        self.is_revoked = True

    @classmethod
    def cleanup_expired_query(cls) -> str:
        """
        Return a query hint for cleaning up expired tokens.

        This is a helper to indicate the cleanup pattern.
        Actual cleanup should be done through the repository.

        Returns:
            str: Description of cleanup approach
        """
        return (
            "DELETE FROM refresh_tokens WHERE expires_at < NOW() OR is_revoked = TRUE"
        )
