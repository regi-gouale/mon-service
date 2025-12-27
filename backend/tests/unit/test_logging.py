"""
Tests for Structured JSON Logging Module.

Tests cover:
- JSON formatter output
- Correlation ID context management
- Request logger functionality
- Text formatter fallback
"""

import json
import logging
from unittest.mock import MagicMock

from app.core.logging import (
    CorrelationIdContext,
    RequestLogger,
    StructuredJsonFormatter,
    TextFormatter,
    correlation_id_context,
    generate_correlation_id,
    get_correlation_id,
    get_logger,
    set_correlation_id,
    setup_logging,
)


class TestCorrelationId:
    """Tests for correlation ID management."""

    def test_generate_correlation_id_returns_uuid(self) -> None:
        """Test that generate_correlation_id returns a valid UUID string."""
        correlation_id = generate_correlation_id()
        assert correlation_id is not None
        assert len(correlation_id) == 36  # UUID format: 8-4-4-4-12
        assert correlation_id.count("-") == 4

    def test_set_and_get_correlation_id(self) -> None:
        """Test setting and getting correlation ID from context."""
        # Initially should be None
        initial = get_correlation_id()
        assert initial is None

        # Set a correlation ID
        token = set_correlation_id("test-correlation-123")

        try:
            assert get_correlation_id() == "test-correlation-123"
        finally:
            # Clean up
            from app.core.logging import correlation_id_var

            correlation_id_var.reset(token)

    def test_correlation_id_context_manager(self) -> None:
        """Test correlation ID context manager."""
        with correlation_id_context("context-test-456") as cid:
            assert cid == "context-test-456"
            assert get_correlation_id() == "context-test-456"

        # Should be reset after context exit
        assert get_correlation_id() is None

    def test_correlation_id_context_generates_id_if_none(self) -> None:
        """Test that context manager generates ID if not provided."""
        with correlation_id_context() as cid:
            assert cid is not None
            assert len(cid) == 36
            assert get_correlation_id() == cid

    def test_correlation_id_context_class_directly(self) -> None:
        """Test CorrelationIdContext class directly."""
        ctx = CorrelationIdContext("direct-test-789")

        assert ctx.correlation_id == "direct-test-789"

        with ctx as cid:
            assert cid == "direct-test-789"

    def test_nested_correlation_id_contexts(self) -> None:
        """Test that nested contexts work correctly."""
        with correlation_id_context("outer-123") as outer_id:
            assert get_correlation_id() == "outer-123"
            assert outer_id == "outer-123"

            with correlation_id_context("inner-456") as inner:
                assert get_correlation_id() == "inner-456"
                assert inner == "inner-456"

            # Should restore outer context
            assert get_correlation_id() == "outer-123"

        assert get_correlation_id() is None


class TestStructuredJsonFormatter:
    """Tests for JSON log formatter."""

    def test_format_basic_log_record(self) -> None:
        """Test basic log record formatting."""
        formatter = StructuredJsonFormatter(
            service_name="test-service",
            environment="test",
        )

        record = logging.LogRecord(
            name="test.logger",
            level=logging.INFO,
            pathname="test.py",
            lineno=10,
            msg="Test message",
            args=(),
            exc_info=None,
        )

        output = formatter.format(record)
        data = json.loads(output)

        assert data["level"] == "INFO"
        assert data["logger"] == "test.logger"
        assert data["message"] == "Test message"
        assert data["service"] == "test-service"
        assert data["environment"] == "test"
        assert "timestamp" in data
        assert "correlation_id" in data

    def test_format_includes_correlation_id(self) -> None:
        """Test that correlation ID is included in log output."""
        formatter = StructuredJsonFormatter()

        with correlation_id_context("log-test-correlation"):
            record = logging.LogRecord(
                name="test",
                level=logging.INFO,
                pathname="test.py",
                lineno=10,
                msg="With correlation",
                args=(),
                exc_info=None,
            )

            output = formatter.format(record)
            data = json.loads(output)

            assert data["correlation_id"] == "log-test-correlation"

    def test_format_includes_location_for_warnings(self) -> None:
        """Test that location info is included for WARNING and above."""
        formatter = StructuredJsonFormatter()

        record = logging.LogRecord(
            name="test",
            level=logging.WARNING,
            pathname="test_file.py",
            lineno=42,
            msg="Warning message",
            args=(),
            exc_info=None,
        )

        output = formatter.format(record)
        data = json.loads(output)

        assert "location" in data
        assert data["location"]["file"] == "test_file.py"
        assert data["location"]["line"] == 42

    def test_format_does_not_include_location_for_info(self) -> None:
        """Test that location is not included for INFO level."""
        formatter = StructuredJsonFormatter()

        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test_file.py",
            lineno=42,
            msg="Info message",
            args=(),
            exc_info=None,
        )

        output = formatter.format(record)
        data = json.loads(output)

        assert "location" not in data

    def test_format_includes_extra_fields(self) -> None:
        """Test that extra fields are included in output."""
        formatter = StructuredJsonFormatter()

        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=10,
            msg="With extras",
            args=(),
            exc_info=None,
        )
        record.user_id = 123
        record.action = "login"

        output = formatter.format(record)
        data = json.loads(output)

        assert data["user_id"] == 123
        assert data["action"] == "login"

    def test_format_handles_exception_info(self) -> None:
        """Test that exception info is included."""
        formatter = StructuredJsonFormatter()

        try:
            raise ValueError("Test error")
        except ValueError:
            import sys

            exc_info = sys.exc_info()

            record = logging.LogRecord(
                name="test",
                level=logging.ERROR,
                pathname="test.py",
                lineno=10,
                msg="Error occurred",
                args=(),
                exc_info=exc_info,
            )

            output = formatter.format(record)
            data = json.loads(output)

            assert "exception" in data
            assert data["exception"]["type"] == "ValueError"
            assert data["exception"]["message"] == "Test error"
            assert "traceback" in data["exception"]


class TestTextFormatter:
    """Tests for text log formatter."""

    def test_format_basic_record(self) -> None:
        """Test basic text formatting."""
        formatter = TextFormatter()

        record = logging.LogRecord(
            name="test.logger",
            level=logging.INFO,
            pathname="test.py",
            lineno=10,
            msg="Test message",
            args=(),
            exc_info=None,
        )

        output = formatter.format(record)

        assert "INFO" in output
        assert "test.logger" in output
        assert "Test message" in output
        assert "correlation_id=" in output

    def test_format_includes_correlation_id(self) -> None:
        """Test that correlation ID is included in text output."""
        formatter = TextFormatter()

        with correlation_id_context("text-log-test"):
            record = logging.LogRecord(
                name="test",
                level=logging.INFO,
                pathname="test.py",
                lineno=10,
                msg="With correlation",
                args=(),
                exc_info=None,
            )

            output = formatter.format(record)

            assert "text-log-test" in output


class TestSetupLogging:
    """Tests for logging setup function."""

    def test_setup_logging_returns_logger(self) -> None:
        """Test that setup_logging returns a logger."""
        logger = setup_logging(
            log_level="DEBUG",
            log_format="json",
            service_name="test",
            environment="test",
        )

        assert isinstance(logger, logging.Logger)

    def test_setup_logging_with_text_format(self) -> None:
        """Test setup with text format."""
        logger = setup_logging(
            log_level="INFO",
            log_format="text",
            service_name="test",
            environment="test",
        )

        assert isinstance(logger, logging.Logger)

    def test_get_logger_returns_named_logger(self) -> None:
        """Test that get_logger returns correctly named logger."""
        logger = get_logger("my.custom.logger")

        assert logger.name == "my.custom.logger"


class TestRequestLogger:
    """Tests for request logger helper."""

    def test_start_request_logs_info(self) -> None:
        """Test that start_request logs request info."""
        mock_logger = MagicMock()
        request_logger = RequestLogger(logger=mock_logger)

        start_time = request_logger.start_request(
            method="GET",
            path="/api/v1/users",
            client_ip="127.0.0.1",
            user_agent="TestAgent/1.0",
        )

        assert start_time > 0
        mock_logger.info.assert_called_once()

        call_args = mock_logger.info.call_args
        assert call_args[0][0] == "Request started"
        assert call_args[1]["extra"]["http_method"] == "GET"
        assert call_args[1]["extra"]["http_path"] == "/api/v1/users"

    def test_end_request_logs_completion(self) -> None:
        """Test that end_request logs completion with timing."""
        mock_logger = MagicMock()
        request_logger = RequestLogger(logger=mock_logger)

        request_logger.end_request(
            method="POST",
            path="/api/v1/auth/login",
            status_code=200,
            start_time=0,  # Using 0 to get a large duration
        )

        mock_logger.log.assert_called_once()
        call_args = mock_logger.log.call_args
        assert call_args[1]["extra"]["http_status"] == 200
        assert "duration_ms" in call_args[1]["extra"]

    def test_end_request_logs_warning_for_4xx(self) -> None:
        """Test that 4xx responses are logged as warnings."""
        mock_logger = MagicMock()
        request_logger = RequestLogger(logger=mock_logger)

        request_logger.end_request(
            method="GET",
            path="/api/v1/unknown",
            status_code=404,
            start_time=0,
        )

        call_args = mock_logger.log.call_args
        assert call_args[0][0] == logging.WARNING

    def test_end_request_logs_error_for_5xx(self) -> None:
        """Test that 5xx responses are logged as errors."""
        mock_logger = MagicMock()
        request_logger = RequestLogger(logger=mock_logger)

        request_logger.end_request(
            method="POST",
            path="/api/v1/process",
            status_code=500,
            start_time=0,
        )

        call_args = mock_logger.log.call_args
        assert call_args[0][0] == logging.ERROR

    def test_log_error_logs_exception(self) -> None:
        """Test that log_error logs exception details."""
        mock_logger = MagicMock()
        request_logger = RequestLogger(logger=mock_logger)

        error = ValueError("Something went wrong")
        request_logger.log_error(
            method="PUT",
            path="/api/v1/update",
            error=error,
            start_time=0,
        )

        mock_logger.exception.assert_called_once()
        call_args = mock_logger.exception.call_args
        assert call_args[1]["extra"]["error_type"] == "ValueError"
        assert call_args[1]["extra"]["error_message"] == "Something went wrong"
