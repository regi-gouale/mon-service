"""
Correlation ID Middleware.

This middleware handles correlation ID generation and propagation
for request tracing across distributed systems.

Features:
- Generates unique correlation ID for each request
- Accepts incoming correlation ID from X-Correlation-ID header
- Adds correlation ID to response headers
- Sets correlation ID in async context for logging
- Logs request/response with timing metrics

Usage:
    from app.core.middleware import CorrelationIdMiddleware

    app.add_middleware(CorrelationIdMiddleware)

Headers:
    Request:  X-Correlation-ID (optional, will generate if missing)
    Response: X-Correlation-ID (always present)
"""

import time
from collections.abc import Callable
from typing import Any

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from starlette.types import ASGIApp

from app.core.logging import (
    RequestLogger,
    generate_correlation_id,
    get_logger,
    set_correlation_id,
)

# Header name for correlation ID
CORRELATION_ID_HEADER = "X-Correlation-ID"

logger = get_logger(__name__)


class CorrelationIdMiddleware(BaseHTTPMiddleware):
    """
    Middleware for handling correlation ID and request logging.

    This middleware:
    1. Extracts or generates a correlation ID for each request
    2. Sets the correlation ID in the async context for logging
    3. Adds the correlation ID to the response headers
    4. Logs request start/end with timing metrics

    Attributes:
        exclude_paths: Paths to exclude from detailed logging (e.g., health checks).
    """

    def __init__(
        self,
        app: ASGIApp,
        exclude_paths: list[str] | None = None,
    ) -> None:
        """
        Initialize the middleware.

        Args:
            app: The ASGI application.
            exclude_paths: List of paths to exclude from detailed logging.
        """
        super().__init__(app)
        self.exclude_paths = exclude_paths or ["/health", "/metrics", "/favicon.ico"]
        self.request_logger = RequestLogger()

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Any]
    ) -> Response:
        """
        Process the request with correlation ID.

        Args:
            request: The incoming HTTP request.
            call_next: The next middleware/handler in the chain.

        Returns:
            The HTTP response with correlation ID header.
        """
        # Extract or generate correlation ID
        correlation_id = request.headers.get(
            CORRELATION_ID_HEADER, generate_correlation_id()
        )

        # Set correlation ID in context for logging
        token = set_correlation_id(correlation_id)

        # Store in request state for access in exception handlers
        request.state.correlation_id = correlation_id

        # Check if path should be excluded from detailed logging
        should_log = request.url.path not in self.exclude_paths

        try:
            # Log request start
            start_time = time.perf_counter()

            if should_log:
                client_ip = self._get_client_ip(request)
                user_agent = request.headers.get("User-Agent")
                self.request_logger.start_request(
                    method=request.method,
                    path=request.url.path,
                    client_ip=client_ip,
                    user_agent=user_agent,
                )

            # Process request
            response = await call_next(request)

            # Log request completion
            if should_log:
                self.request_logger.end_request(
                    method=request.method,
                    path=request.url.path,
                    status_code=response.status_code,
                    start_time=start_time,
                )

            # Add correlation ID to response headers
            response.headers[CORRELATION_ID_HEADER] = correlation_id

            return response  # type: ignore[no-any-return]

        except Exception as exc:
            # Log the error
            if should_log:
                self.request_logger.log_error(
                    method=request.method,
                    path=request.url.path,
                    error=exc,
                    start_time=start_time,
                )
            raise

        finally:
            # Reset context (important for connection reuse)
            from app.core.logging import correlation_id_var

            correlation_id_var.reset(token)

    def _get_client_ip(self, request: Request) -> str | None:
        """
        Extract client IP from request, considering proxies.

        Args:
            request: The HTTP request.

        Returns:
            Client IP address or None.
        """
        # Check for forwarded headers (from reverse proxy)
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            # Take the first IP in the chain (original client)
            return forwarded.split(",")[0].strip()

        # Check for real IP header
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip

        # Fall back to direct client
        if request.client:
            return request.client.host

        return None


def get_correlation_id_from_request(request: Request) -> str:
    """
    Get the correlation ID from a request.

    Args:
        request: The HTTP request.

    Returns:
        The correlation ID string.
    """
    return getattr(request.state, "correlation_id", "unknown")
