"""
Alembic Environment Configuration.

This module configures Alembic for async SQLAlchemy with PostgreSQL.
It supports both offline (SQL generation) and online (database connection) modes.

The database URL is loaded from environment variables via the app configuration,
ensuring consistency with the main application.
"""

import asyncio
import os
from logging.config import fileConfig

from dotenv import load_dotenv
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context

# Load environment variables from .env file
# This ensures DATABASE_URL and other required vars are available
# interpolate=True enables ${VAR} substitution
load_dotenv(interpolate=True)

# Import the settings to get database URL from environment
from app.core.config import settings

# Import Base to access metadata for autogenerate support
from app.core.database import Base

# Import all models here so they are registered with Base.metadata
# This ensures Alembic can detect all tables for autogenerate
# Example:
# from app.models.user import User
# from app.models.organization import Organization

# Alembic Config object
config = context.config

# Override sqlalchemy.url with the actual database URL from settings
# Convert asyncpg URL to standard postgresql for offline mode compatibility
database_url = str(settings.database_url)
config.set_main_option("sqlalchemy.url", database_url)

# Configure Python logging from the config file
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Target metadata for autogenerate support
# This is the MetaData object from your declarative base
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """
    Run migrations in 'offline' mode.

    This configures the context with just a URL and not an Engine.
    Calls to context.execute() emit the given string to the script output.

    This is useful for generating SQL scripts without a database connection.
    """
    url = config.get_main_option("sqlalchemy.url")

    # For offline mode, we need to convert async URL to sync format
    if url and url.startswith("postgresql+asyncpg://"):
        url = url.replace("postgresql+asyncpg://", "postgresql://")

    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection) -> None:
    """
    Execute migrations using the provided connection.

    This function is run synchronously within the async context.

    Args:
        connection: SQLAlchemy database connection
    """
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """
    Run migrations in 'online' mode with async engine.

    Creates an async Engine and associates a connection with the context.
    The connection is used to run all migrations within a transaction.
    """
    # Create async engine configuration
    configuration = config.get_section(config.config_ini_section) or {}

    # Ensure we use the async driver
    if "sqlalchemy.url" in configuration:
        url = configuration["sqlalchemy.url"]
        # Ensure async URL format
        if url.startswith("postgresql://"):
            configuration["sqlalchemy.url"] = url.replace(
                "postgresql://", "postgresql+asyncpg://"
            )

    connectable = async_engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """
    Run migrations in 'online' mode.

    This is the entry point for online migrations.
    It delegates to the async migration runner.
    """
    asyncio.run(run_async_migrations())


# Determine which mode to run in based on context
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
