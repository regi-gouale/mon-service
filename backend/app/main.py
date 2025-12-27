"""
FastAPI Application Entry Point.

This module contains the main FastAPI application instance with:
- CORS middleware configuration
- Logging middleware with correlation ID
- Exception handlers
- Health check endpoint
- Startup/shutdown events (lifespan)
- API v1 routes

Usage:
    uvicorn app.main:app --reload
"""

import logging
import sys
import time
import uuid
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


# =============================================================================
# Logging Configuration
# =============================================================================
def setup_logging() -> logging.Logger:
    """
    Configure structured logging for the application.

    Returns:
        Logger: Configured application logger.
    """
    log_level = getattr(logging, settings.log_level, logging.INFO)

    # Configure root logger
    logging.basicConfig(
        level=log_level,
        format=(
            '{"timestamp": "%(asctime)s", "level": "%(levelname)s", '
            '"logger": "%(name)s", "message": "%(message)s"}'
            if settings.log_format == "json"
            else "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        ),
        datefmt="%Y-%m-%dT%H:%M:%S%z",
        stream=sys.stdout,
        force=True,
    )

    logger = logging.getLogger("app")
    logger.setLevel(log_level)

    return logger


logger = setup_logging()


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

    # Configure CORS
    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=settings.cors_allow_credentials,
        allow_methods=settings.cors_allow_methods,
        allow_headers=settings.cors_allow_headers,
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
# Logging Middleware
# =============================================================================
app = create_application()


@app.middleware("http")
async def logging_middleware(request: Request, call_next: Any) -> Any:
    """
    Middleware for request logging with correlation ID.

    Adds a correlation ID to each request for tracing and logs
    request/response details with timing information.
    """
    # Generate or extract correlation ID
    correlation_id = request.headers.get("X-Correlation-ID", str(uuid.uuid4()))
    request.state.correlation_id = correlation_id

    # Log request
    start_time = time.perf_counter()
    logger.info(
        f"Request started | method={request.method} | path={request.url.path} | "
        f"correlation_id={correlation_id}"
    )

    try:
        response = await call_next(request)

        # Calculate duration
        duration_ms = (time.perf_counter() - start_time) * 1000

        # Log response
        logger.info(
            f"Request completed | method={request.method} | path={request.url.path} | "
            f"status={response.status_code} | duration_ms={duration_ms:.2f} | "
            f"correlation_id={correlation_id}"
        )

        # Add correlation ID to response headers
        response.headers["X-Correlation-ID"] = correlation_id

        return response

    except Exception as exc:
        duration_ms = (time.perf_counter() - start_time) * 1000
        logger.exception(
            f"Request failed | method={request.method} | path={request.url.path} | "
            f"duration_ms={duration_ms:.2f} | correlation_id={correlation_id} | "
            f"error={exc!s}"
        )
        raise
