"""
Unit tests for the User model.

Tests cover:
- Model instantiation and default values
- Field constraints and validation
- Password hashing and verification
- Soft delete functionality
- String representations
- Database operations (CRUD)
- Relationship with Organization
"""

from datetime import datetime
from uuid import UUID

import pytest
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.organization import Organization
from app.models.user import User, UserRole


class TestUserModel:
    """Test suite for User model instantiation and methods."""

    def test_user_instantiation(self) -> None:
        """Test that User can be instantiated with required fields."""
        user = User(
            email="test@example.com",
            first_name="John",
            last_name="Doe",
        )

        assert user.email == "test@example.com"
        assert user.first_name == "John"
        assert user.last_name == "Doe"
        assert user.password_hash is None
        assert user.phone is None
        assert user.avatar_url is None
        assert user.organization_id is None

    def test_user_with_all_fields(self) -> None:
        """Test User with all optional fields."""
        user = User(
            email="full@example.com",
            first_name="Jane",
            last_name="Smith",
            phone="+33612345678",
            avatar_url="https://example.com/avatar.png",
            role=UserRole.ADMIN,
            email_verified=True,
            is_active=True,
        )

        assert user.email == "full@example.com"
        assert user.first_name == "Jane"
        assert user.last_name == "Smith"
        assert user.phone == "+33612345678"
        assert user.avatar_url == "https://example.com/avatar.png"
        assert user.role == UserRole.ADMIN
        assert user.email_verified is True
        assert user.is_active is True

    def test_user_repr(self) -> None:
        """Test __repr__ method."""
        user = User(
            email="test@example.com",
            first_name="John",
            last_name="Doe",
        )
        repr_str = repr(user)
        assert "User" in repr_str
        assert "test@example.com" in repr_str

    def test_user_str(self) -> None:
        """Test __str__ method returns full name."""
        user = User(
            email="test@example.com",
            first_name="John",
            last_name="Doe",
        )
        assert str(user) == "John Doe"

    def test_user_full_name_property(self) -> None:
        """Test full_name property."""
        user = User(
            email="test@example.com",
            first_name="John",
            last_name="Doe",
        )
        assert user.full_name == "John Doe"

    def test_user_role_enum(self) -> None:
        """Test UserRole enum values."""
        assert UserRole.ADMIN.value == "admin"
        assert UserRole.MANAGER.value == "manager"
        assert UserRole.MEMBER.value == "member"
        assert UserRole.GUEST.value == "guest"


class TestUserPassword:
    """Test suite for password hashing and verification."""

    def test_set_password(self) -> None:
        """Test password hashing."""
        user = User(
            email="test@example.com",
            first_name="John",
            last_name="Doe",
        )
        user.set_password("SecurePassword123!")

        assert user.password_hash is not None
        assert user.password_hash != "SecurePassword123!"
        assert user.password_hash.startswith("$2b$")  # bcrypt prefix

    def test_check_password_correct(self) -> None:
        """Test password verification with correct password."""
        user = User(
            email="test@example.com",
            first_name="John",
            last_name="Doe",
        )
        user.set_password("SecurePassword123!")

        assert user.check_password("SecurePassword123!") is True

    def test_check_password_incorrect(self) -> None:
        """Test password verification with incorrect password."""
        user = User(
            email="test@example.com",
            first_name="John",
            last_name="Doe",
        )
        user.set_password("SecurePassword123!")

        assert user.check_password("WrongPassword") is False

    def test_check_password_no_hash(self) -> None:
        """Test password verification when no password is set (OAuth user)."""
        user = User(
            email="oauth@example.com",
            first_name="OAuth",
            last_name="User",
        )

        assert user.check_password("AnyPassword") is False


class TestUserSoftDelete:
    """Test suite for soft delete functionality."""

    def test_is_deleted_property_false(self) -> None:
        """Test is_deleted property when user is not deleted."""
        user = User(
            email="test@example.com",
            first_name="John",
            last_name="Doe",
        )
        assert user.is_deleted is False

    def test_soft_delete(self) -> None:
        """Test soft delete method."""
        user = User(
            email="test@example.com",
            first_name="John",
            last_name="Doe",
        )
        user.soft_delete()

        assert user.is_deleted is True
        assert user.deleted_at is not None
        assert user.is_active is False

    def test_restore(self) -> None:
        """Test restore method after soft delete."""
        user = User(
            email="test@example.com",
            first_name="John",
            last_name="Doe",
        )
        user.soft_delete()
        user.restore()

        assert user.is_deleted is False
        assert user.deleted_at is None
        assert user.is_active is True


class TestUserDatabase:
    """Database integration tests for User model."""

    @pytest.mark.asyncio
    async def test_create_user(self, async_session: AsyncSession) -> None:
        """Test creating a user in the database."""
        user = User(
            email="test@example.com",
            first_name="John",
            last_name="Doe",
        )
        user.set_password("SecurePassword123!")

        async_session.add(user)
        await async_session.commit()
        await async_session.refresh(user)

        assert user.id is not None
        UUID(user.id)  # Verify valid UUID
        assert user.created_at is not None
        assert user.updated_at is not None
        assert isinstance(user.created_at, datetime)
        assert user.is_active is True
        assert user.email_verified is False
        assert user.role == UserRole.MEMBER

    @pytest.mark.asyncio
    async def test_read_user(self, async_session: AsyncSession) -> None:
        """Test reading a user from the database."""
        user = User(
            email="read@example.com",
            first_name="Read",
            last_name="User",
        )
        async_session.add(user)
        await async_session.commit()

        stmt = select(User).where(User.email == "read@example.com")
        result = await async_session.execute(stmt)
        fetched_user = result.scalar_one()

        assert fetched_user.email == "read@example.com"
        assert fetched_user.first_name == "Read"
        assert fetched_user.last_name == "User"

    @pytest.mark.asyncio
    async def test_update_user(self, async_session: AsyncSession) -> None:
        """Test updating a user in the database."""
        user = User(
            email="update@example.com",
            first_name="Update",
            last_name="User",
        )
        async_session.add(user)
        await async_session.commit()

        original_created_at = user.created_at

        user.first_name = "Updated"
        user.email_verified = True
        await async_session.commit()
        await async_session.refresh(user)

        assert user.first_name == "Updated"
        assert user.email_verified is True
        assert user.created_at == original_created_at

    @pytest.mark.asyncio
    async def test_delete_user(self, async_session: AsyncSession) -> None:
        """Test deleting a user from the database."""
        user = User(
            email="delete@example.com",
            first_name="Delete",
            last_name="User",
        )
        async_session.add(user)
        await async_session.commit()
        user_id = user.id

        await async_session.delete(user)
        await async_session.commit()

        stmt = select(User).where(User.id == user_id)
        result = await async_session.execute(stmt)
        assert result.scalar_one_or_none() is None

    @pytest.mark.asyncio
    async def test_email_unique_constraint(self, async_session: AsyncSession) -> None:
        """Test that email must be unique."""
        user1 = User(
            email="unique@example.com",
            first_name="First",
            last_name="User",
        )
        async_session.add(user1)
        await async_session.commit()

        user2 = User(
            email="unique@example.com",
            first_name="Second",
            last_name="User",
        )
        async_session.add(user2)

        with pytest.raises(IntegrityError):
            await async_session.commit()

    @pytest.mark.asyncio
    async def test_email_not_null_constraint(self, async_session: AsyncSession) -> None:
        """Test that email is required."""
        user = User(
            email=None,  # type: ignore
            first_name="No",
            last_name="Email",
        )
        async_session.add(user)

        with pytest.raises(IntegrityError):
            await async_session.commit()

    @pytest.mark.asyncio
    async def test_first_name_not_null_constraint(
        self, async_session: AsyncSession
    ) -> None:
        """Test that first_name is required."""
        user = User(
            email="test@example.com",
            first_name=None,  # type: ignore
            last_name="User",
        )
        async_session.add(user)

        with pytest.raises(IntegrityError):
            await async_session.commit()

    @pytest.mark.asyncio
    async def test_last_name_not_null_constraint(
        self, async_session: AsyncSession
    ) -> None:
        """Test that last_name is required."""
        user = User(
            email="test@example.com",
            first_name="Test",
            last_name=None,  # type: ignore
        )
        async_session.add(user)

        with pytest.raises(IntegrityError):
            await async_session.commit()


class TestUserOrganizationRelationship:
    """Test User-Organization relationship."""

    @pytest.mark.asyncio
    async def test_user_with_organization(self, async_session: AsyncSession) -> None:
        """Test creating a user with an organization."""
        org = Organization(
            name="Test Church",
            slug="test-church-user",
        )
        async_session.add(org)
        await async_session.commit()
        await async_session.refresh(org)

        user = User(
            email="org-user@example.com",
            first_name="Org",
            last_name="User",
            organization_id=org.id,
        )
        async_session.add(user)
        await async_session.commit()
        await async_session.refresh(user)

        assert user.organization_id == org.id

    @pytest.mark.asyncio
    async def test_organization_users_relationship(
        self, async_session: AsyncSession
    ) -> None:
        """Test accessing users from organization."""
        org = Organization(
            name="Relationship Test",
            slug="relationship-test",
        )
        async_session.add(org)
        await async_session.commit()
        await async_session.refresh(org)

        user1 = User(
            email="user1@example.com",
            first_name="User",
            last_name="One",
            organization_id=org.id,
        )
        user2 = User(
            email="user2@example.com",
            first_name="User",
            last_name="Two",
            organization_id=org.id,
        )
        async_session.add_all([user1, user2])
        await async_session.commit()

        # Refresh organization to load users
        await async_session.refresh(org)

        assert len(org.users) == 2
        emails = [u.email for u in org.users]
        assert "user1@example.com" in emails
        assert "user2@example.com" in emails

    @pytest.mark.asyncio
    async def test_user_organization_back_populates(
        self, async_session: AsyncSession
    ) -> None:
        """Test accessing organization from user."""
        org = Organization(
            name="Back Populates Test",
            slug="back-populates-test",
        )
        async_session.add(org)
        await async_session.commit()

        user = User(
            email="backpop@example.com",
            first_name="Back",
            last_name="Populates",
            organization_id=org.id,
        )
        async_session.add(user)
        await async_session.commit()
        await async_session.refresh(user)

        assert user.organization is not None
        assert user.organization.name == "Back Populates Test"

    @pytest.mark.asyncio
    async def test_query_users_by_organization(
        self, async_session: AsyncSession
    ) -> None:
        """Test querying users by organization."""
        org = Organization(
            name="Query Test",
            slug="query-test-org",
        )
        async_session.add(org)
        await async_session.commit()

        user = User(
            email="query-org@example.com",
            first_name="Query",
            last_name="User",
            organization_id=org.id,
        )
        async_session.add(user)
        await async_session.commit()

        stmt = select(User).where(User.organization_id == org.id)
        result = await async_session.execute(stmt)
        users = result.scalars().all()

        assert len(users) == 1
        assert users[0].email == "query-org@example.com"

    @pytest.mark.asyncio
    async def test_user_with_sample_data(
        self,
        async_session: AsyncSession,
        sample_user_data: dict,
    ) -> None:
        """Test creating user with fixture data."""
        user = User(
            email=sample_user_data["email"],
            first_name=sample_user_data["first_name"],
            last_name=sample_user_data["last_name"],
        )
        user.set_password(sample_user_data["password"])

        async_session.add(user)
        await async_session.commit()
        await async_session.refresh(user)

        assert user.email == sample_user_data["email"]
        assert user.check_password(sample_user_data["password"]) is True
