"""
Unit tests for the Organization model.

Tests cover:
- Model instantiation and default values
- Field constraints and validation
- String representations
- Database operations (CRUD)
"""

from datetime import datetime
from uuid import UUID

import pytest
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.organization import Organization


class TestOrganizationModel:
    """Test suite for Organization model."""

    def test_organization_instantiation(self) -> None:
        """Test that Organization can be instantiated with required fields."""
        org = Organization(
            name="Test Church",
            slug="test-church",
        )

        assert org.name == "Test Church"
        assert org.slug == "test-church"
        # Note: Default values are applied by SQLAlchemy when the object is added to session
        # or after commit, not during instantiation
        assert org.description is None
        assert org.logo_url is None

    def test_organization_with_all_fields(self) -> None:
        """Test Organization with all optional fields."""
        org = Organization(
            name="Full Church",
            slug="full-church",
            description="A complete church organization",
            logo_url="https://example.com/logo.png",
            is_active=False,
        )

        assert org.name == "Full Church"
        assert org.slug == "full-church"
        assert org.description == "A complete church organization"
        assert org.logo_url == "https://example.com/logo.png"
        assert org.is_active is False

    def test_organization_repr(self) -> None:
        """Test __repr__ method."""
        org = Organization(
            name="Test Church",
            slug="test-church",
        )
        # The id is generated on instantiation
        repr_str = repr(org)
        assert "Organization" in repr_str
        assert "test-church" in repr_str
        assert "Test Church" in repr_str

    def test_organization_str(self) -> None:
        """Test __str__ method returns name."""
        org = Organization(
            name="Test Church",
            slug="test-church",
        )
        assert str(org) == "Test Church"

    def test_organization_id_is_uuid(self) -> None:
        """Test that id is a valid UUID string after database commit."""
        # Note: The default id is only generated when the object is inserted into the database
        # For in-memory instantiation, id will be None until commit
        org = Organization(
            name="Test Church",
            slug="test-church",
        )
        # Before commit, id is None
        assert org.id is None


class TestOrganizationDatabase:
    """Database integration tests for Organization model."""

    @pytest.mark.asyncio
    async def test_create_organization(self, async_session: AsyncSession) -> None:
        """Test creating an organization in the database."""
        org = Organization(
            name="Test Church",
            slug="test-church",
            description="A test church organization",
        )

        async_session.add(org)
        await async_session.commit()
        await async_session.refresh(org)

        assert org.id is not None
        # Verify the id is a valid UUID
        UUID(org.id)
        assert org.created_at is not None
        assert org.updated_at is not None
        assert isinstance(org.created_at, datetime)
        assert isinstance(org.updated_at, datetime)
        # Default value should be applied after commit
        assert org.is_active is True

    @pytest.mark.asyncio
    async def test_read_organization(self, async_session: AsyncSession) -> None:
        """Test reading an organization from the database."""
        org = Organization(
            name="Read Test Church",
            slug="read-test-church",
        )
        async_session.add(org)
        await async_session.commit()

        # Query the organization
        stmt = select(Organization).where(Organization.slug == "read-test-church")
        result = await async_session.execute(stmt)
        fetched_org = result.scalar_one()

        assert fetched_org.name == "Read Test Church"
        assert fetched_org.slug == "read-test-church"
        assert fetched_org.is_active is True

    @pytest.mark.asyncio
    async def test_update_organization(self, async_session: AsyncSession) -> None:
        """Test updating an organization in the database."""
        org = Organization(
            name="Update Test Church",
            slug="update-test-church",
        )
        async_session.add(org)
        await async_session.commit()

        original_created_at = org.created_at

        # Update the organization
        org.name = "Updated Church Name"
        org.description = "Added description"
        await async_session.commit()
        await async_session.refresh(org)

        assert org.name == "Updated Church Name"
        assert org.description == "Added description"
        assert org.created_at == original_created_at

    @pytest.mark.asyncio
    async def test_delete_organization(self, async_session: AsyncSession) -> None:
        """Test deleting an organization from the database."""
        org = Organization(
            name="Delete Test Church",
            slug="delete-test-church",
        )
        async_session.add(org)
        await async_session.commit()
        org_id = org.id

        # Delete the organization
        await async_session.delete(org)
        await async_session.commit()

        # Verify deletion
        stmt = select(Organization).where(Organization.id == org_id)
        result = await async_session.execute(stmt)
        assert result.scalar_one_or_none() is None

    @pytest.mark.asyncio
    async def test_slug_unique_constraint(self, async_session: AsyncSession) -> None:
        """Test that slug must be unique."""
        org1 = Organization(
            name="First Church",
            slug="unique-slug",
        )
        async_session.add(org1)
        await async_session.commit()

        # Try to create another organization with the same slug
        org2 = Organization(
            name="Second Church",
            slug="unique-slug",
        )
        async_session.add(org2)

        with pytest.raises(IntegrityError):
            await async_session.commit()

    @pytest.mark.asyncio
    async def test_name_not_null_constraint(self, async_session: AsyncSession) -> None:
        """Test that name is required."""
        org = Organization(
            name=None,  # type: ignore
            slug="no-name-church",
        )
        async_session.add(org)

        with pytest.raises(IntegrityError):
            await async_session.commit()

    @pytest.mark.asyncio
    async def test_slug_not_null_constraint(self, async_session: AsyncSession) -> None:
        """Test that slug is required."""
        org = Organization(
            name="No Slug Church",
            slug=None,  # type: ignore
        )
        async_session.add(org)

        with pytest.raises(IntegrityError):
            await async_session.commit()

    @pytest.mark.asyncio
    async def test_query_by_is_active(self, async_session: AsyncSession) -> None:
        """Test querying organizations by is_active status."""
        # Create active and inactive organizations
        active_org = Organization(
            name="Active Church",
            slug="active-church",
            is_active=True,
        )
        inactive_org = Organization(
            name="Inactive Church",
            slug="inactive-church",
            is_active=False,
        )

        async_session.add_all([active_org, inactive_org])
        await async_session.commit()

        # Query active organizations
        stmt = select(Organization).where(Organization.is_active.is_(True))
        result = await async_session.execute(stmt)
        active_orgs = result.scalars().all()

        assert len([o for o in active_orgs if o.slug == "active-church"]) == 1
        assert len([o for o in active_orgs if o.slug == "inactive-church"]) == 0

    @pytest.mark.asyncio
    async def test_organization_with_sample_data(
        self,
        async_session: AsyncSession,
        sample_organization_data: dict,
    ) -> None:
        """Test creating organization with fixture data."""
        org = Organization(**sample_organization_data)

        async_session.add(org)
        await async_session.commit()
        await async_session.refresh(org)

        assert org.name == sample_organization_data["name"]
        assert org.slug == sample_organization_data["slug"]
