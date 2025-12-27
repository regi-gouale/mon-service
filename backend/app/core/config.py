"""
Application Configuration.

This module contains the application settings using Pydantic Settings
for environment variable management and validation.

Usage:
    from app.core.config import settings

    print(settings.app_name)
    print(settings.database_url)
"""

from functools import lru_cache
from typing import Annotated, Literal

from pydantic import Field, PostgresDsn, computed_field, field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.

    Environment variables take priority over default values.
    A .env file is loaded if present in the working directory.

    Attributes:
        app_name: Application display name
        app_env: Current environment (development, staging, production)
        debug: Enable debug mode (verbose logging, detailed errors)
        database_url: PostgreSQL connection string
        redis_url: Redis connection string
        secret_key: Secret key for JWT signing and encryption
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ========================================================================
    # Application Settings
    # ========================================================================
    app_name: str = Field(default="Church Team Management", alias="APP_NAME")
    app_version: str = Field(default="0.1.0", alias="APP_VERSION")
    app_env: Literal["development", "staging", "production"] = Field(
        default="development", alias="APP_ENV"
    )
    debug: bool = Field(default=False, alias="DEBUG")

    # API Configuration
    api_v1_prefix: str = Field(default="/api/v1", alias="API_V1_PREFIX")

    # ========================================================================
    # Security / JWT Settings
    # ========================================================================
    secret_key: str = Field(..., alias="SECRET_KEY")
    jwt_algorithm: str = Field(default="HS256", alias="JWT_ALGORITHM")
    access_token_expire_minutes: int = Field(
        default=15, alias="ACCESS_TOKEN_EXPIRE_MINUTES"
    )
    refresh_token_expire_days: int = Field(default=7, alias="REFRESH_TOKEN_EXPIRE_DAYS")

    # ========================================================================
    # Database Settings
    # ========================================================================
    database_url: PostgresDsn = Field(..., alias="DATABASE_URL")
    database_pool_size: int = Field(default=5, alias="DATABASE_POOL_SIZE")
    database_max_overflow: int = Field(default=10, alias="DATABASE_MAX_OVERFLOW")
    database_echo: bool = Field(default=False, alias="DATABASE_ECHO")

    # ========================================================================
    # Redis Settings
    # ========================================================================
    redis_url: str = Field(default="redis://localhost:6379/0", alias="REDIS_URL")
    redis_max_connections: int = Field(default=10, alias="REDIS_MAX_CONNECTIONS")

    # ========================================================================
    # CORS Settings
    # ========================================================================
    cors_origins: Annotated[list[str], NoDecode] = Field(
        default=["http://localhost:3000"], alias="CORS_ORIGINS"
    )
    cors_allow_credentials: bool = Field(default=True, alias="CORS_ALLOW_CREDENTIALS")
    cors_allow_methods: list[str] = Field(default=["*"], alias="CORS_ALLOW_METHODS")
    cors_allow_headers: list[str] = Field(default=["*"], alias="CORS_ALLOW_HEADERS")

    # ========================================================================
    # Email (SMTP) Settings
    # ========================================================================
    smtp_host: str = Field(default="localhost", alias="SMTP_HOST")
    smtp_port: int = Field(default=1025, alias="SMTP_PORT")
    smtp_user: str | None = Field(default=None, alias="SMTP_USER")
    smtp_password: str | None = Field(default=None, alias="SMTP_PASSWORD")
    smtp_from_email: str = Field(default="noreply@example.com", alias="SMTP_FROM_EMAIL")
    smtp_from_name: str = Field(
        default="Church Team Management", alias="SMTP_FROM_NAME"
    )
    smtp_tls: bool = Field(default=False, alias="SMTP_TLS")
    smtp_ssl: bool = Field(default=False, alias="SMTP_SSL")

    # ========================================================================
    # S3 / MinIO Settings
    # ========================================================================
    s3_endpoint_url: str | None = Field(default=None, alias="S3_ENDPOINT_URL")
    s3_access_key: str | None = Field(default=None, alias="S3_ACCESS_KEY")
    s3_secret_key: str | None = Field(default=None, alias="S3_SECRET_KEY")
    s3_bucket_name: str = Field(default="uploads", alias="S3_BUCKET_NAME")
    s3_region: str = Field(default="eu-west-1", alias="S3_REGION")
    s3_use_ssl: bool = Field(default=True, alias="S3_USE_SSL")

    # ========================================================================
    # Celery Settings
    # ========================================================================
    celery_broker_url: str = Field(
        default="redis://localhost:6379/1", alias="CELERY_BROKER_URL"
    )
    celery_result_backend: str = Field(
        default="redis://localhost:6379/2", alias="CELERY_RESULT_BACKEND"
    )
    celery_task_always_eager: bool = Field(
        default=False, alias="CELERY_TASK_ALWAYS_EAGER"
    )
    celery_task_time_limit: int = Field(
        default=300, alias="CELERY_TASK_TIME_LIMIT"
    )  # 5 minutes

    # ========================================================================
    # OAuth Settings
    # ========================================================================
    google_client_id: str | None = Field(default=None, alias="GOOGLE_CLIENT_ID")
    google_client_secret: str | None = Field(default=None, alias="GOOGLE_CLIENT_SECRET")

    # ========================================================================
    # Rate Limiting Settings
    # ========================================================================
    rate_limit_per_minute: int = Field(default=60, alias="RATE_LIMIT_PER_MINUTE")
    rate_limit_auth_per_minute: int = Field(
        default=10, alias="RATE_LIMIT_AUTH_PER_MINUTE"
    )

    # ========================================================================
    # Logging Settings
    # ========================================================================
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field(
        default="INFO", alias="LOG_LEVEL"
    )
    log_format: Literal["json", "text"] = Field(default="json", alias="LOG_FORMAT")

    # ========================================================================
    # Computed Properties
    # ========================================================================
    @computed_field  # type: ignore[prop-decorator]
    @property
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.app_env == "development"

    @computed_field  # type: ignore[prop-decorator]
    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.app_env == "production"

    @computed_field  # type: ignore[prop-decorator]
    @property
    def database_url_str(self) -> str:
        """Get database URL as string for SQLAlchemy."""
        return str(self.database_url)

    # ========================================================================
    # Validators
    # ========================================================================
    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: str | list[str]) -> list[str]:
        """Parse CORS origins from comma-separated string or list."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v

    @field_validator("secret_key", mode="after")
    @classmethod
    def validate_secret_key_length(cls, v: str) -> str:
        """Ensure secret key has sufficient length for security."""
        if len(v) < 32:
            raise ValueError("SECRET_KEY must be at least 32 characters long")
        return v


@lru_cache
def get_settings() -> Settings:
    """
    Get cached application settings.

    Returns:
        Settings: Application settings singleton instance.

    Note:
        Settings are cached after first load. To reload settings,
        call `get_settings.cache_clear()` first.
    """
    return Settings()


# Singleton settings instance for easy import
settings = get_settings()
