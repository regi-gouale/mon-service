"""
Structured JSON Logging Configuration.

This module provides structured JSON logging with correlation ID support
for request tracing across distributed systems.

Features:
- JSON formatted logs (compatible with Loki/ELK stack)
- Correlation ID per request for distributed tracing
- Contextual logging with extra fields
- Performance metrics (duration, status codes)
- Support for both JSON and text formats

Usage:
    from app.core.logging import get_logger, correlation_id_context

    logger = get_logger(__name__)
    logger.info("Processing request", extra={"user_id": 123})

    # With correlation ID context
    with correlation_id_context("abc-123"):
        logger.info("This log will include correlation_id=abc-123")
"""

import contextvars
import json
import logging
import sys
import time
import uuid
from datetime import UTC, datetime
from typing import Any

# Context variable for correlation ID (thread-safe for async)
correlation_id_var: contextvars.ContextVar[str | None] = contextvars.ContextVar(
    "correlation_id", default=None
)


def get_correlation_id() -> str | None:
    """
    Get the current correlation ID from context.

    Returns:
        Optional correlation ID string, or None if not set.
    """
    return correlation_id_var.get()


def set_correlation_id(correlation_id: str | None) -> contextvars.Token[str | None]:
    """
    Set the correlation ID in context.

    Args:
        correlation_id: The correlation ID to set.

    Returns:
        Token that can be used to reset the context.
    """
    return correlation_id_var.set(correlation_id)


def generate_correlation_id() -> str:
    """
    Generate a new unique correlation ID.

    Returns:
        UUID string for correlation ID.
    """
    return str(uuid.uuid4())


class CorrelationIdContext:
    """Context manager for correlation ID scope."""

    def __init__(self, correlation_id: str | None = None) -> None:
        """
        Initialize the context with a correlation ID.

        Args:
            correlation_id: The correlation ID to use. If None, generates a new one.
        """
        self.correlation_id = correlation_id or generate_correlation_id()
        self._token: contextvars.Token[str | None] | None = None

    def __enter__(self) -> str:
        """Enter the context and set the correlation ID."""
        self._token = set_correlation_id(self.correlation_id)
        return self.correlation_id

    def __exit__(self, *args: object) -> None:
        """Exit the context and reset the correlation ID."""
        if self._token is not None:
            correlation_id_var.reset(self._token)


def correlation_id_context(correlation_id: str | None = None) -> CorrelationIdContext:
    """
    Create a context manager for correlation ID scope.

    Args:
        correlation_id: Optional correlation ID. If None, generates a new one.

    Returns:
        CorrelationIdContext manager.

    Example:
        with correlation_id_context("req-123"):
            logger.info("Processing...")
    """
    return CorrelationIdContext(correlation_id)


class StructuredJsonFormatter(logging.Formatter):
    """
    JSON formatter for structured logging.

    Outputs logs in JSON format compatible with log aggregation systems
    like Loki, ELK Stack, Datadog, etc.

    Output format:
    {
        "timestamp": "2025-12-27T10:30:00.000Z",
        "level": "INFO",
        "logger": "app.services.auth",
        "message": "User authenticated",
        "correlation_id": "abc-123-def",
        "service": "church-team-management",
        "environment": "production",
        ...extra_fields
    }
    """

    def __init__(
        self,
        service_name: str = "church-team-management",
        environment: str = "development",
        include_stack_trace: bool = True,
    ) -> None:
        """
        Initialize the JSON formatter.

        Args:
            service_name: Name of the service for log identification.
            environment: Current environment (development, staging, production).
            include_stack_trace: Whether to include stack traces for exceptions.
        """
        super().__init__()
        self.service_name = service_name
        self.environment = environment
        self.include_stack_trace = include_stack_trace

    def format(self, record: logging.LogRecord) -> str:
        """
        Format the log record as JSON.

        Args:
            record: The log record to format.

        Returns:
            JSON string representation of the log.
        """
        # Base log structure
        log_data: dict[str, Any] = {
            "timestamp": datetime.now(UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "correlation_id": get_correlation_id(),
            "service": self.service_name,
            "environment": self.environment,
        }

        # Add source location for debugging
        if record.levelno >= logging.WARNING:
            log_data["location"] = {
                "file": record.filename,
                "line": record.lineno,
                "function": record.funcName,
            }

        # Add exception info if present
        if record.exc_info and self.include_stack_trace:
            log_data["exception"] = {
                "type": record.exc_info[0].__name__ if record.exc_info[0] else None,
                "message": str(record.exc_info[1]) if record.exc_info[1] else None,
                "traceback": self.formatException(record.exc_info),
            }

        # Add extra fields from the log record
        # Exclude standard LogRecord attributes
        standard_attrs = {
            "name",
            "msg",
            "args",
            "created",
            "filename",
            "funcName",
            "levelname",
            "levelno",
            "lineno",
            "module",
            "msecs",
            "pathname",
            "process",
            "processName",
            "relativeCreated",
            "stack_info",
            "exc_info",
            "exc_text",
            "thread",
            "threadName",
            "taskName",
            "message",
        }

        for key, value in record.__dict__.items():
            if key not in standard_attrs and not key.startswith("_"):
                # Handle non-serializable objects
                try:
                    json.dumps(value)
                    log_data[key] = value
                except (TypeError, ValueError):
                    log_data[key] = str(value)

        return json.dumps(log_data, ensure_ascii=False, default=str)


class TextFormatter(logging.Formatter):
    """
    Human-readable text formatter for development.

    Includes correlation ID in the log output for consistency.
    """

    def __init__(self) -> None:
        """Initialize the text formatter."""
        super().__init__(
            fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s | correlation_id=%(correlation_id)s",
            datefmt="%Y-%m-%dT%H:%M:%S%z",
        )

    def format(self, record: logging.LogRecord) -> str:
        """
        Format the log record as text.

        Args:
            record: The log record to format.

        Returns:
            Formatted text string.
        """
        # Add correlation_id to record if not present
        if not hasattr(record, "correlation_id"):
            record.correlation_id = get_correlation_id() or "-"
        return super().format(record)


def setup_logging(
    log_level: str = "INFO",
    log_format: str = "json",
    service_name: str = "church-team-management",
    environment: str = "development",
) -> logging.Logger:
    """
    Configure structured logging for the application.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL).
        log_format: Output format ("json" or "text").
        service_name: Name of the service for log identification.
        environment: Current environment.

    Returns:
        Configured root logger.

    Example:
        setup_logging(
            log_level="INFO",
            log_format="json",
            service_name="my-service",
            environment="production",
        )
    """
    # Get numeric log level
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)

    # Create handler
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(numeric_level)

    # Set formatter based on format type
    formatter: logging.Formatter
    if log_format.lower() == "json":
        formatter = StructuredJsonFormatter(
            service_name=service_name,
            environment=environment,
        )
    else:
        formatter = TextFormatter()

    handler.setFormatter(formatter)

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)

    # Remove existing handlers to avoid duplicates
    root_logger.handlers.clear()
    root_logger.addHandler(handler)

    # Reduce noise from third-party libraries
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.error").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("asyncio").setLevel(logging.WARNING)

    return root_logger


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance with the given name.

    Args:
        name: Logger name (typically __name__).

    Returns:
        Configured logger instance.

    Example:
        logger = get_logger(__name__)
        logger.info("Hello", extra={"user_id": 123})
    """
    return logging.getLogger(name)


class RequestLogger:
    """
    Helper class for logging HTTP request/response details.

    Provides structured logging for API requests with timing,
    status codes, and correlation IDs.
    """

    def __init__(self, logger: logging.Logger | None = None) -> None:
        """
        Initialize the request logger.

        Args:
            logger: Optional logger instance. Creates one if not provided.
        """
        self.logger = logger or get_logger("app.requests")
        self._start_time: float | None = None

    def start_request(
        self,
        method: str,
        path: str,
        client_ip: str | None = None,
        user_agent: str | None = None,
    ) -> float:
        """
        Log the start of an HTTP request.

        Args:
            method: HTTP method (GET, POST, etc.).
            path: Request path.
            client_ip: Client IP address.
            user_agent: Client user agent.

        Returns:
            Start timestamp for duration calculation.
        """
        self._start_time = time.perf_counter()

        self.logger.info(
            "Request started",
            extra={
                "event": "request_started",
                "http_method": method,
                "http_path": path,
                "client_ip": client_ip,
                "user_agent": user_agent,
            },
        )

        return self._start_time

    def end_request(
        self,
        method: str,
        path: str,
        status_code: int,
        start_time: float | None = None,
    ) -> None:
        """
        Log the completion of an HTTP request.

        Args:
            method: HTTP method.
            path: Request path.
            status_code: HTTP response status code.
            start_time: Request start timestamp (uses stored value if not provided).
        """
        start = start_time or self._start_time or time.perf_counter()
        duration_ms = (time.perf_counter() - start) * 1000

        log_level = logging.INFO if status_code < 400 else logging.WARNING
        if status_code >= 500:
            log_level = logging.ERROR

        self.logger.log(
            log_level,
            "Request completed",
            extra={
                "event": "request_completed",
                "http_method": method,
                "http_path": path,
                "http_status": status_code,
                "duration_ms": round(duration_ms, 2),
            },
        )

    def log_error(
        self,
        method: str,
        path: str,
        error: Exception,
        start_time: float | None = None,
    ) -> None:
        """
        Log a request error.

        Args:
            method: HTTP method.
            path: Request path.
            error: Exception that occurred.
            start_time: Request start timestamp.
        """
        start = start_time or self._start_time or time.perf_counter()
        duration_ms = (time.perf_counter() - start) * 1000

        self.logger.exception(
            "Request failed",
            extra={
                "event": "request_failed",
                "http_method": method,
                "http_path": path,
                "error_type": type(error).__name__,
                "error_message": str(error),
                "duration_ms": round(duration_ms, 2),
            },
        )
