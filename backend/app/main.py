"""
FastAPI Application Entry Point.

This module contains the main FastAPI application instance with:
- CORS middleware configuration
- Structured JSON logging with correlation ID
- Exception handlers
- Health check endpoint
- Startup/shutdown events (lifespan)
- API v1 routes

Usage:
    uvicorn app.main:app --reload
"""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.v1.routes import router as api_v1_router
from app.core.config import settings
from app.core.exceptions import (
    AlreadyExistsError,
    AppException,
    ForbiddenError,
    NotFoundError,
    UnauthorizedError,
    ValidationError,
)
from app.core.logging import get_logger, setup_logging
from app.core.middleware import CorrelationIdMiddleware

# =============================================================================
# Logging Configuration
# =============================================================================
# Initialize structured logging
setup_logging(
    log_level=settings.log_level,
    log_format=settings.log_format,
    service_name=settings.app_name.lower().replace(" ", "-"),
    environment=settings.app_env,
)

logger = get_logger(__name__)


# =============================================================================
# Lifespan Events
# =============================================================================
@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncGenerator[None]:
    """
    Application lifespan context manager.

    Handles startup and shutdown events for the application.
    Use this to initialize and cleanup resources like database connections,
    cache clients, etc.
    """
    # Startup
    logger.info(
        f"Starting {settings.app_name} v{settings.app_version} "
        f"in {settings.app_env} environment"
    )

    if settings.debug:
        logger.warning("Debug mode is enabled - do not use in production!")

    # TODO: Initialize database connection pool
    # TODO: Initialize Redis connection
    # TODO: Initialize other resources

    yield

    # Shutdown
    logger.info(f"Shutting down {settings.app_name}")

    # TODO: Close database connection pool
    # TODO: Close Redis connection
    # TODO: Cleanup other resources


# =============================================================================
# Application Factory
# =============================================================================
def create_application() -> FastAPI:
    """
    Application factory to create and configure the FastAPI instance.

    Returns:
        FastAPI: Configured FastAPI application.
    """
    application = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="Church Team Management SaaS - Backend API",
        docs_url="/docs" if settings.is_development else None,
        redoc_url="/redoc" if settings.is_development else None,
        openapi_url="/openapi.json" if settings.is_development else None,
        lifespan=lifespan,
    )

    # Configure CORS (must be added before other middleware)
    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=settings.cors_allow_credentials,
        allow_methods=settings.cors_allow_methods,
        allow_headers=[*settings.cors_allow_headers, "X-Correlation-ID"],
        expose_headers=["X-Correlation-ID"],
    )

    # Add correlation ID middleware for request tracing
    application.add_middleware(
        CorrelationIdMiddleware,
        exclude_paths=["/health", "/metrics", "/favicon.ico"],
    )

    # Register exception handlers
    register_exception_handlers(application)

    # Register routes
    register_routes(application)

    return application


# =============================================================================
# Exception Handlers
# =============================================================================
def register_exception_handlers(application: FastAPI) -> None:
    """Register custom exception handlers for the application."""

    @application.exception_handler(AppException)
    async def app_exception_handler(
        request: Request, exc: AppException
    ) -> JSONResponse:
        """Handle application-specific exceptions."""
        correlation_id = getattr(request.state, "correlation_id", "unknown")
        logger.error(
            f"AppException: {exc.message} | correlation_id={correlation_id} | "
            f"details={exc.details}"
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": "internal_error",
                "message": exc.message,
                "details": exc.details,
                "correlation_id": correlation_id,
            },
        )

    @application.exception_handler(NotFoundError)
    async def not_found_handler(request: Request, exc: NotFoundError) -> JSONResponse:
        """Handle not found exceptions."""
        correlation_id = getattr(request.state, "correlation_id", "unknown")
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "error": "not_found",
                "message": exc.message,
                "correlation_id": correlation_id,
            },
        )

    @application.exception_handler(AlreadyExistsError)
    async def already_exists_handler(
        request: Request, exc: AlreadyExistsError
    ) -> JSONResponse:
        """Handle already exists exceptions."""
        correlation_id = getattr(request.state, "correlation_id", "unknown")
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={
                "error": "already_exists",
                "message": exc.message,
                "correlation_id": correlation_id,
            },
        )

    @application.exception_handler(UnauthorizedError)
    async def unauthorized_handler(
        request: Request, exc: UnauthorizedError
    ) -> JSONResponse:
        """Handle unauthorized exceptions."""
        correlation_id = getattr(request.state, "correlation_id", "unknown")
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={
                "error": "unauthorized",
                "message": exc.message,
                "correlation_id": correlation_id,
            },
            headers={"WWW-Authenticate": "Bearer"},
        )

    @application.exception_handler(ForbiddenError)
    async def forbidden_handler(request: Request, exc: ForbiddenError) -> JSONResponse:
        """Handle forbidden exceptions."""
        correlation_id = getattr(request.state, "correlation_id", "unknown")
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={
                "error": "forbidden",
                "message": exc.message,
                "correlation_id": correlation_id,
            },
        )

    @application.exception_handler(ValidationError)
    async def validation_error_handler(
        request: Request, exc: ValidationError
    ) -> JSONResponse:
        """Handle validation exceptions."""
        correlation_id = getattr(request.state, "correlation_id", "unknown")
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "error": "validation_error",
                "message": exc.message,
                "details": exc.details,
                "correlation_id": correlation_id,
            },
        )

    @application.exception_handler(Exception)
    async def generic_exception_handler(
        request: Request, exc: Exception
    ) -> JSONResponse:
        """Handle unexpected exceptions."""
        correlation_id = getattr(request.state, "correlation_id", "unknown")
        logger.exception(
            f"Unhandled exception: {exc!s} | correlation_id={correlation_id}"
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": "internal_error",
                "message": "An unexpected error occurred",
                "correlation_id": correlation_id,
            },
        )


# =============================================================================
# Routes Registration
# =============================================================================
def register_routes(application: FastAPI) -> None:
    """Register all application routes."""

    @application.get(
        "/health",
        tags=["Health"],
        summary="Health Check",
        response_model=dict[str, Any],
    )
    async def health_check() -> dict[str, Any]:
        """
        Health check endpoint.

        Returns the application health status including:
        - Application name and version
        - Current environment
        - Status indicator

        Use this endpoint for:
        - Kubernetes liveness/readiness probes
        - Load balancer health checks
        - Monitoring systems
        """
        return {
            "status": "healthy",
            "app_name": settings.app_name,
            "version": settings.app_version,
            "environment": settings.app_env,
        }

    # Include API v1 routes
    application.include_router(
        api_v1_router,
        prefix=settings.api_v1_prefix,
        tags=["API v1"],
    )


# =============================================================================
# Application Instance
# =============================================================================
app = create_application()
