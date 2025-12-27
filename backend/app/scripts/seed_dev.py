"""
Development Database Seed Script.

This script populates the database with test data for development purposes.
It is idempotent - running it multiple times will not create duplicate data.

Usage:
    python -m app.scripts.seed_dev

Environment Variables:
    SEED_ADMIN_PASSWORD: Password for admin user (default: auto-generated)
    SEED_MANAGER_PASSWORD: Password for manager user (default: auto-generated)
    SEED_MEMBER_PASSWORD: Password for member users (default: auto-generated)
    SEED_GUEST_PASSWORD: Password for guest user (default: auto-generated)

Data created:
    - 1 Organization (Test Church)
    - 5 Users (1 admin + 4 members)
    - Future: Departments, Members, Services (when models are available)
"""

import asyncio
import hashlib
import os
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

# Add backend to path for module imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import async_session_maker
from app.models import Organization, User, UserRole

# =============================================================================
# Password Generation
# =============================================================================


def get_dev_password(role: str) -> str:
    """
    Get password for a role from environment or generate a deterministic one.

    For development only - generates predictable passwords based on role.
    In CI/CD, set environment variables for specific passwords.

    Args:
        role: The user role (admin, manager, member, guest)

    Returns:
        str: The password for the role
    """
    env_var = f"SEED_{role.upper()}_PASSWORD"
    env_password = os.environ.get(env_var)

    if env_password:
        return env_password

    # Generate a deterministic password for dev (based on role + secret)
    # This avoids hardcoding passwords while keeping dev predictable
    secret = os.environ.get("SECRET_KEY", "dev-seed-secret")
    hash_input = f"{role}:{secret}:dev-seed"
    hash_value = hashlib.sha256(hash_input.encode()).hexdigest()[:8]
    return f"Dev{role.capitalize()}{hash_value}!"


# =============================================================================
# Seed Data Definitions
# =============================================================================

ORGANIZATION_DATA: dict[str, Any] = {
    "name": "Test Church",
    "slug": "test-church",
    "description": "A test church organization for development purposes.",
    "logo_url": None,
    "is_active": True,
}


def get_users_data() -> list[dict[str, Any]]:
    """
    Get users data with passwords from environment or generated.

    Returns:
        list[dict[str, Any]]: List of user data dictionaries
    """
    return [
        {
            "email": "admin@test-church.org",
            "password": get_dev_password("admin"),
            "first_name": "Admin",
            "last_name": "User",
            "phone": "+33612345678",
            "role": UserRole.ADMIN,
            "email_verified": True,
            "is_active": True,
        },
        {
            "email": "manager@test-church.org",
            "password": get_dev_password("manager"),
            "first_name": "Marie",
            "last_name": "Manager",
            "phone": "+33612345679",
            "role": UserRole.MANAGER,
            "email_verified": True,
            "is_active": True,
        },
        {
            "email": "member1@test-church.org",
            "password": get_dev_password("member"),
            "first_name": "Pierre",
            "last_name": "Membre",
            "phone": "+33612345680",
            "role": UserRole.MEMBER,
            "email_verified": True,
            "is_active": True,
        },
        {
            "email": "member2@test-church.org",
            "password": get_dev_password("member"),
            "first_name": "Sophie",
            "last_name": "Dupont",
            "phone": "+33612345681",
            "role": UserRole.MEMBER,
            "email_verified": True,
            "is_active": True,
        },
        {
            "email": "guest@test-church.org",
            "password": get_dev_password("guest"),
            "first_name": "Jean",
            "last_name": "Invité",
            "phone": None,
            "role": UserRole.GUEST,
            "email_verified": False,
            "is_active": True,
        },
    ]


# Future seed data (when models are available)
# DEPARTMENTS_DATA = [
#     {
#         "name": "Praise & Worship",
#         "slug": "praise-worship",
#         "description": "Music and worship team",
#     },
#     {
#         "name": "Ushers",
#         "slug": "ushers",
#         "description": "Welcome and hospitality team",
#     },
# ]


# =============================================================================
# Seed Functions
# =============================================================================


async def seed_organization(session: AsyncSession) -> Organization:
    """
    Create or get the test organization.

    Returns:
        Organization: The test organization instance.
    """
    # Check if organization already exists
    result = await session.execute(
        select(Organization).where(Organization.slug == ORGANIZATION_DATA["slug"])
    )
    org = result.scalar_one_or_none()

    if org:
        print(f"  ⏩ Organization '{org.name}' already exists (id: {org.id})")
        return org

    # Create new organization
    org = Organization(**ORGANIZATION_DATA)
    session.add(org)
    await session.flush()

    print(f"  ✅ Created organization '{org.name}' (id: {org.id})")
    return org


async def seed_users(session: AsyncSession, organization: Organization) -> list[User]:
    """
    Create test users for the organization.

    Args:
        session: The database session.
        organization: The organization to associate users with.

    Returns:
        list[User]: List of created or existing users.
    """
    users = []
    users_data = get_users_data()

    for user_data in users_data:
        # Check if user already exists
        result = await session.execute(
            select(User).where(User.email == user_data["email"])
        )
        user = result.scalar_one_or_none()

        if user:
            print(f"  ⏩ User '{user.email}' already exists (id: {user.id})")
            users.append(user)
            continue

        # Create new user - extract password before spreading user_data
        password = user_data["password"]
        user = User(
            organization_id=organization.id,
            email=user_data["email"],
            first_name=user_data["first_name"],
            last_name=user_data["last_name"],
            phone=user_data["phone"],
            role=user_data["role"],
            email_verified=user_data["email_verified"],
            is_active=user_data["is_active"],
        )
        user.set_password(password)

        session.add(user)
        await session.flush()

        print(f"  ✅ Created user '{user.email}' ({user.role.value}) (id: {user.id})")
        users.append(user)

    return users


# Future seed functions (when models are available)
# async def seed_departments(
#     session: AsyncSession,
#     organization: Organization
# ) -> list:
#     """Create test departments."""
#     pass
#
# async def seed_services(
#     session: AsyncSession,
#     department: Any
# ) -> list:
#     """Create test services for next month."""
#     pass


# =============================================================================
# Main Seed Function
# =============================================================================


async def seed_database() -> None:
    """
    Main function to seed the database with test data.

    This function is idempotent - it checks for existing data before creating.
    """
    print("\n🌱 Starting database seed...\n")
    print(f"Timestamp: {datetime.now(UTC).isoformat()}")
    print("-" * 50)

    async with async_session_maker() as session:
        try:
            # Seed organization
            print("\n📍 Seeding Organization...")
            organization = await seed_organization(session)

            # Seed users
            print("\n👥 Seeding Users...")
            users = await seed_users(session, organization)

            # Future: Seed departments (T2.1)
            # print("\n🏢 Seeding Departments...")
            # departments = await seed_departments(session, organization)

            # Future: Seed services (T3.1)
            # print("\n📅 Seeding Services...")
            # services = await seed_services(session, departments[0])

            # Commit all changes
            await session.commit()

            # Summary
            print("\n" + "-" * 50)
            print("✨ Seed completed successfully!")
            print("   - Organization: 1")
            print(f"   - Users: {len(users)}")
            # print(f"   - Departments: {len(departments)}")
            # print(f"   - Services: {len(services)}")
            print()

        except Exception as e:
            await session.rollback()
            print(f"\n❌ Error during seed: {e}")
            raise


async def clear_database() -> None:
    """
    Clear all data from the database.

    WARNING: This will delete all data! Use with caution.
    """
    print("\n🗑️  Clearing database...\n")

    async with async_session_maker() as session:
        try:
            # Delete in reverse order of dependencies
            await session.execute(
                User.__table__.delete()  # type: ignore[attr-defined]
            )
            await session.execute(
                Organization.__table__.delete()  # type: ignore[attr-defined]
            )
            await session.commit()

            print("✅ Database cleared successfully!")

        except Exception as e:
            await session.rollback()
            print(f"\n❌ Error clearing database: {e}")
            raise


# =============================================================================
# CLI Entry Point
# =============================================================================


async def run_seed(clear: bool = False, only_clear: bool = False) -> None:
    """
    Run the seed process.

    Args:
        clear: If True, clear database before seeding.
        only_clear: If True, only clear database (no seeding).
    """
    if only_clear or clear:
        await clear_database()

    if not only_clear:
        await seed_database()


def main() -> None:
    """CLI entry point for the seed script."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Seed the database with test data.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python -m app.scripts.seed_dev           # Seed database
    python -m app.scripts.seed_dev --clear   # Clear and reseed
    python -m app.scripts.seed_dev --only-clear  # Only clear (no seed)
        """,
    )
    parser.add_argument(
        "--clear",
        action="store_true",
        help="Clear database before seeding",
    )
    parser.add_argument(
        "--only-clear",
        action="store_true",
        help="Only clear database (do not seed)",
    )

    args = parser.parse_args()

    asyncio.run(run_seed(clear=args.clear, only_clear=args.only_clear))


if __name__ == "__main__":
    main()
