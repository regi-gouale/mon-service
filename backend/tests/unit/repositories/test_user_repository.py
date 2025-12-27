"""
Unit tests for the UserRepository.

Tests cover:
- CRUD operations (create, read, update, delete)
- Error handling (not found, duplicate)
- Soft delete and restore functionality
- Query methods (by email, by organization)
"""

from datetime import UTC, datetime

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AlreadyExistsError, NotFoundError
from app.models.user import User, UserRole
from app.repositories.user_repository import UserRepository


@pytest_asyncio.fixture
async def user_repository(async_session: AsyncSession) -> UserRepository:
    """Create a UserRepository instance with test session."""
    return UserRepository(async_session)


@pytest_asyncio.fixture
async def sample_user(
    user_repository: UserRepository,
    async_session: AsyncSession,
) -> User:
    """Create a sample user for testing."""
    user = await user_repository.create(
        email="test@example.com",
        password_hash="hashed_password_123",
        first_name="John",
        last_name="Doe",
    )
    await async_session.commit()
    return user


class TestUserRepositoryCreate:
    """Tests for UserRepository.create method."""

    async def test_create_user_success(
        self,
        user_repository: UserRepository,
        async_session: AsyncSession,
    ) -> None:
        """Test successful user creation."""
        user = await user_repository.create(
            email="newuser@example.com",
            password_hash="hashed_password",
            first_name="Jane",
            last_name="Smith",
        )
        await async_session.commit()

        assert user is not None
        assert user.id is not None
        assert user.email == "newuser@example.com"
        assert user.first_name == "Jane"
        assert user.last_name == "Smith"
        assert user.password_hash == "hashed_password"
        assert user.role == UserRole.MEMBER
        assert user.is_active is True
        assert user.email_verified is False
        assert user.deleted_at is None

    async def test_create_user_email_normalized(
        self,
        user_repository: UserRepository,
        async_session: AsyncSession,
    ) -> None:
        """Test that email is normalized (lowercase, stripped)."""
        user = await user_repository.create(
            email="  TEST@EXAMPLE.COM  ",
            password_hash="hashed",
            first_name="Test",
            last_name="User",
        )
        await async_session.commit()

        assert user.email == "test@example.com"

    async def test_create_user_with_all_fields(
        self,
        user_repository: UserRepository,
        async_session: AsyncSession,
    ) -> None:
        """Test user creation with all optional fields."""
        user = await user_repository.create(
            email="full@example.com",
            password_hash="hashed",
            first_name="Full",
            last_name="User",
            organization_id=None,
            role=UserRole.ADMIN,
            phone="+1234567890",
            avatar_url="https://example.com/avatar.jpg",
            email_verified=True,
            is_active=True,
            notification_preferences={"email": True, "push": False},
        )
        await async_session.commit()

        assert user.role == UserRole.ADMIN
        assert user.phone == "+1234567890"
        assert user.avatar_url == "https://example.com/avatar.jpg"
        assert user.email_verified is True
        assert user.notification_preferences == {"email": True, "push": False}

    async def test_create_user_without_password(
        self,
        user_repository: UserRepository,
        async_session: AsyncSession,
    ) -> None:
        """Test creating OAuth user without password."""
        user = await user_repository.create(
            email="oauth@example.com",
            password_hash=None,
            first_name="OAuth",
            last_name="User",
        )
        await async_session.commit()

        assert user.password_hash is None

    async def test_create_user_duplicate_email_raises_error(
        self,
        user_repository: UserRepository,
        sample_user: User,  # noqa: ARG002
    ) -> None:
        """Test that creating user with duplicate email raises error."""
        with pytest.raises(AlreadyExistsError) as exc_info:
            await user_repository.create(
                email="test@example.com",  # Same as sample_user
                password_hash="another_hash",
                first_name="Duplicate",
                last_name="User",
            )

        assert "email" in exc_info.value.message.lower()
        assert "test@example.com" in exc_info.value.message


class TestUserRepositoryGetById:
    """Tests for UserRepository.get_by_id method."""

    async def test_get_by_id_success(
        self,
        user_repository: UserRepository,
        sample_user: User,
    ) -> None:
        """Test successful retrieval by ID."""
        user = await user_repository.get_by_id(sample_user.id)

        assert user is not None
        assert user.id == sample_user.id
        assert user.email == sample_user.email

    async def test_get_by_id_not_found_returns_none(
        self,
        user_repository: UserRepository,
    ) -> None:
        """Test that non-existent ID returns None."""
        user = await user_repository.get_by_id("non-existent-id")

        assert user is None

    async def test_get_by_id_excludes_deleted_by_default(
        self,
        user_repository: UserRepository,
        sample_user: User,
        async_session: AsyncSession,
    ) -> None:
        """Test that soft-deleted users are excluded by default."""
        await user_repository.delete(sample_user.id)
        await async_session.commit()

        user = await user_repository.get_by_id(sample_user.id)

        assert user is None

    async def test_get_by_id_includes_deleted_when_requested(
        self,
        user_repository: UserRepository,
        sample_user: User,
        async_session: AsyncSession,
    ) -> None:
        """Test that soft-deleted users can be included."""
        await user_repository.delete(sample_user.id)
        await async_session.commit()

        user = await user_repository.get_by_id(sample_user.id, include_deleted=True)

        assert user is not None
        assert user.deleted_at is not None

    async def test_get_by_id_or_raise_success(
        self,
        user_repository: UserRepository,
        sample_user: User,
    ) -> None:
        """Test get_by_id_or_raise returns user when found."""
        user = await user_repository.get_by_id_or_raise(sample_user.id)

        assert user.id == sample_user.id

    async def test_get_by_id_or_raise_not_found(
        self,
        user_repository: UserRepository,
    ) -> None:
        """Test get_by_id_or_raise raises NotFoundError."""
        with pytest.raises(NotFoundError) as exc_info:
            await user_repository.get_by_id_or_raise("non-existent-id")

        assert "User" in exc_info.value.message


class TestUserRepositoryGetByEmail:
    """Tests for UserRepository.get_by_email method."""

    async def test_get_by_email_success(
        self,
        user_repository: UserRepository,
        sample_user: User,  # noqa: ARG002
    ) -> None:
        """Test successful retrieval by email."""
        user = await user_repository.get_by_email("test@example.com")

        assert user is not None
        assert user.email == "test@example.com"

    async def test_get_by_email_normalized(
        self,
        user_repository: UserRepository,
        sample_user: User,  # noqa: ARG002
    ) -> None:
        """Test that email search is case-insensitive."""
        user = await user_repository.get_by_email("  TEST@EXAMPLE.COM  ")

        assert user is not None
        assert user.email == "test@example.com"

    async def test_get_by_email_not_found_returns_none(
        self,
        user_repository: UserRepository,
    ) -> None:
        """Test that non-existent email returns None."""
        user = await user_repository.get_by_email("nonexistent@example.com")

        assert user is None

    async def test_get_by_email_excludes_deleted_by_default(
        self,
        user_repository: UserRepository,
        sample_user: User,
        async_session: AsyncSession,
    ) -> None:
        """Test that soft-deleted users are excluded by default."""
        await user_repository.delete(sample_user.id)
        await async_session.commit()

        user = await user_repository.get_by_email("test@example.com")

        assert user is None

    async def test_get_by_email_or_raise_success(
        self,
        user_repository: UserRepository,
        sample_user: User,  # noqa: ARG002
    ) -> None:
        """Test get_by_email_or_raise returns user when found."""
        user = await user_repository.get_by_email_or_raise("test@example.com")

        assert user.email == "test@example.com"

    async def test_get_by_email_or_raise_not_found(
        self,
        user_repository: UserRepository,
    ) -> None:
        """Test get_by_email_or_raise raises NotFoundError."""
        with pytest.raises(NotFoundError):
            await user_repository.get_by_email_or_raise("nonexistent@example.com")


class TestUserRepositoryUpdate:
    """Tests for UserRepository.update method."""

    async def test_update_single_field(
        self,
        user_repository: UserRepository,
        sample_user: User,
        async_session: AsyncSession,
    ) -> None:
        """Test updating a single field."""
        updated_user = await user_repository.update(
            sample_user.id,
            first_name="Updated",
        )
        await async_session.commit()

        assert updated_user.first_name == "Updated"
        assert updated_user.last_name == sample_user.last_name  # Unchanged

    async def test_update_multiple_fields(
        self,
        user_repository: UserRepository,
        sample_user: User,
        async_session: AsyncSession,
    ) -> None:
        """Test updating multiple fields."""
        updated_user = await user_repository.update(
            sample_user.id,
            first_name="NewFirst",
            last_name="NewLast",
            phone="+1234567890",
        )
        await async_session.commit()

        assert updated_user.first_name == "NewFirst"
        assert updated_user.last_name == "NewLast"
        assert updated_user.phone == "+1234567890"

    async def test_update_email_normalized(
        self,
        user_repository: UserRepository,
        sample_user: User,
        async_session: AsyncSession,
    ) -> None:
        """Test that updated email is normalized."""
        updated_user = await user_repository.update(
            sample_user.id,
            email="  NEWEMAIL@EXAMPLE.COM  ",
        )
        await async_session.commit()

        assert updated_user.email == "newemail@example.com"

    async def test_update_no_changes(
        self,
        user_repository: UserRepository,
        sample_user: User,
    ) -> None:
        """Test update with no changes returns user unchanged."""
        updated_user = await user_repository.update(sample_user.id)

        assert updated_user.id == sample_user.id
        assert updated_user.first_name == sample_user.first_name

    async def test_update_not_found_raises_error(
        self,
        user_repository: UserRepository,
    ) -> None:
        """Test updating non-existent user raises NotFoundError."""
        with pytest.raises(NotFoundError):
            await user_repository.update(
                "non-existent-id",
                first_name="Test",
            )

    async def test_update_duplicate_email_raises_error(
        self,
        user_repository: UserRepository,
        sample_user: User,  # noqa: ARG002
        async_session: AsyncSession,
    ) -> None:
        """Test updating to duplicate email raises error."""
        # Create another user
        other_user = await user_repository.create(
            email="other@example.com",
            password_hash="hash",
            first_name="Other",
            last_name="User",
        )
        await async_session.commit()

        with pytest.raises(AlreadyExistsError):
            await user_repository.update(
                other_user.id,
                email="test@example.com",  # Same as sample_user
            )

    async def test_update_role(
        self,
        user_repository: UserRepository,
        sample_user: User,
        async_session: AsyncSession,
    ) -> None:
        """Test updating user role."""
        updated_user = await user_repository.update(
            sample_user.id,
            role=UserRole.ADMIN,
        )
        await async_session.commit()

        assert updated_user.role == UserRole.ADMIN


class TestUserRepositoryDelete:
    """Tests for UserRepository.delete method."""

    async def test_soft_delete(
        self,
        user_repository: UserRepository,
        sample_user: User,
        async_session: AsyncSession,
    ) -> None:
        """Test soft delete marks user as deleted."""
        result = await user_repository.delete(sample_user.id)
        await async_session.commit()

        assert result is True

        # User should not be found with default query
        user = await user_repository.get_by_id(sample_user.id)
        assert user is None

        # But should be found when including deleted
        user = await user_repository.get_by_id(sample_user.id, include_deleted=True)
        assert user is not None
        assert user.deleted_at is not None
        assert user.is_active is False

    async def test_hard_delete(
        self,
        user_repository: UserRepository,
        sample_user: User,
        async_session: AsyncSession,
    ) -> None:
        """Test hard delete permanently removes user."""
        result = await user_repository.delete(sample_user.id, hard_delete=True)
        await async_session.commit()

        assert result is True

        # User should not exist at all
        user = await user_repository.get_by_id(sample_user.id, include_deleted=True)
        assert user is None

    async def test_delete_not_found_raises_error(
        self,
        user_repository: UserRepository,
    ) -> None:
        """Test deleting non-existent user raises NotFoundError."""
        with pytest.raises(NotFoundError):
            await user_repository.delete("non-existent-id")


class TestUserRepositoryRestore:
    """Tests for UserRepository.restore method."""

    async def test_restore_deleted_user(
        self,
        user_repository: UserRepository,
        sample_user: User,
        async_session: AsyncSession,
    ) -> None:
        """Test restoring a soft-deleted user."""
        # First delete
        await user_repository.delete(sample_user.id)
        await async_session.commit()

        # Then restore
        restored_user = await user_repository.restore(sample_user.id)
        await async_session.commit()

        assert restored_user.deleted_at is None
        assert restored_user.is_active is True

        # Should now be findable
        user = await user_repository.get_by_id(sample_user.id)
        assert user is not None

    async def test_restore_non_deleted_user(
        self,
        user_repository: UserRepository,
        sample_user: User,
    ) -> None:
        """Test restoring a user that wasn't deleted returns user unchanged."""
        restored_user = await user_repository.restore(sample_user.id)

        assert restored_user.deleted_at is None
        assert restored_user.id == sample_user.id


class TestUserRepositoryHelpers:
    """Tests for helper methods."""

    async def test_exists_by_email_true(
        self,
        user_repository: UserRepository,
        sample_user: User,  # noqa: ARG002
    ) -> None:
        """Test exists_by_email returns True for existing email."""
        exists = await user_repository.exists_by_email("test@example.com")

        assert exists is True

    async def test_exists_by_email_false(
        self,
        user_repository: UserRepository,
    ) -> None:
        """Test exists_by_email returns False for non-existing email."""
        exists = await user_repository.exists_by_email("nonexistent@example.com")

        assert exists is False

    async def test_exists_by_email_case_insensitive(
        self,
        user_repository: UserRepository,
        sample_user: User,  # noqa: ARG002
    ) -> None:
        """Test exists_by_email is case-insensitive."""
        exists = await user_repository.exists_by_email("TEST@EXAMPLE.COM")

        assert exists is True

    async def test_update_last_login(
        self,
        user_repository: UserRepository,
        sample_user: User,
        async_session: AsyncSession,
    ) -> None:
        """Test updating last login timestamp."""
        before = datetime.now(UTC)
        updated_user = await user_repository.update_last_login(sample_user.id)
        await async_session.commit()
        after = datetime.now(UTC)

        assert updated_user.last_login_at is not None
        # Convert to UTC if timezone-naive (SQLite returns naive datetimes)
        last_login = updated_user.last_login_at
        if last_login.tzinfo is None:
            last_login = last_login.replace(tzinfo=UTC)
        assert before <= last_login <= after

    async def test_verify_email(
        self,
        user_repository: UserRepository,
        sample_user: User,
        async_session: AsyncSession,
    ) -> None:
        """Test marking email as verified."""
        assert sample_user.email_verified is False

        updated_user = await user_repository.verify_email(sample_user.id)
        await async_session.commit()

        assert updated_user.email_verified is True


class TestUserRepositoryListAndCount:
    """Tests for list and count methods."""

    async def test_list_by_organization_empty(
        self,
        user_repository: UserRepository,
    ) -> None:
        """Test listing users for organization with no users."""
        users = await user_repository.list_by_organization("org-123")

        assert users == []

    async def test_count_by_organization_zero(
        self,
        user_repository: UserRepository,
    ) -> None:
        """Test counting users for organization with no users."""
        count = await user_repository.count_by_organization("org-123")

        assert count == 0
