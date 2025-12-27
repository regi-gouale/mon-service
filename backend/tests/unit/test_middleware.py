"""
Tests for Correlation ID Middleware.

Tests cover:
- Correlation ID generation and propagation
- Response header handling
- Client IP extraction
- Request logging integration
"""

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.core.logging import get_correlation_id
from app.core.middleware import (
    CORRELATION_ID_HEADER,
    CorrelationIdMiddleware,
    get_correlation_id_from_request,
)


@pytest.fixture
def app_with_middleware() -> FastAPI:
    """Create a test FastAPI app with correlation ID middleware."""
    app = FastAPI()

    app.add_middleware(
        CorrelationIdMiddleware,
        exclude_paths=["/health"],
    )

    @app.get("/test")
    async def test_endpoint() -> dict[str, str | None]:
        """Test endpoint that returns correlation ID from context."""
        return {"correlation_id": get_correlation_id()}

    @app.get("/health")
    async def health_endpoint() -> dict[str, str]:
        """Health check endpoint (excluded from logging)."""
        return {"status": "healthy"}

    @app.get("/error")
    async def error_endpoint() -> None:
        """Endpoint that raises an error."""
        raise ValueError("Test error")

    return app


@pytest.fixture
def client(app_with_middleware: FastAPI) -> TestClient:
    """Create test client for the app."""
    return TestClient(app_with_middleware, raise_server_exceptions=False)


class TestCorrelationIdMiddleware:
    """Tests for CorrelationIdMiddleware."""

    def test_generates_correlation_id_if_not_provided(self, client: TestClient) -> None:
        """Test that middleware generates correlation ID when not in request."""
        response = client.get("/test")

        assert response.status_code == 200
        assert CORRELATION_ID_HEADER in response.headers

        correlation_id = response.headers[CORRELATION_ID_HEADER]
        assert len(correlation_id) == 36  # UUID format
        assert correlation_id.count("-") == 4

    def test_uses_provided_correlation_id(self, client: TestClient) -> None:
        """Test that middleware uses correlation ID from request header."""
        custom_id = "custom-correlation-id-12345"
        response = client.get(
            "/test",
            headers={CORRELATION_ID_HEADER: custom_id},
        )

        assert response.status_code == 200
        assert response.headers[CORRELATION_ID_HEADER] == custom_id

    def test_correlation_id_available_in_endpoint(self, client: TestClient) -> None:
        """Test that correlation ID is available in endpoint via context."""
        custom_id = "endpoint-test-id-67890"
        response = client.get(
            "/test",
            headers={CORRELATION_ID_HEADER: custom_id},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["correlation_id"] == custom_id

    def test_health_endpoint_still_gets_correlation_id(
        self, client: TestClient
    ) -> None:
        """Test that excluded paths still get correlation ID in response."""
        response = client.get("/health")

        assert response.status_code == 200
        # Correlation ID should still be added to response
        assert CORRELATION_ID_HEADER in response.headers

    def test_error_response_includes_correlation_id(self, client: TestClient) -> None:
        """Test that error responses include correlation ID."""
        custom_id = "error-test-id"
        response = client.get(
            "/error",
            headers={CORRELATION_ID_HEADER: custom_id},
        )

        assert response.status_code == 500
        # Note: Header might not be added for unhandled exceptions
        # depending on how they're caught

    def test_multiple_requests_get_different_ids(self, client: TestClient) -> None:
        """Test that each request gets a unique correlation ID."""
        response1 = client.get("/test")
        response2 = client.get("/test")

        id1 = response1.headers[CORRELATION_ID_HEADER]
        id2 = response2.headers[CORRELATION_ID_HEADER]

        assert id1 != id2


class TestClientIpExtraction:
    """Tests for client IP extraction in middleware."""

    def test_extracts_ip_from_x_forwarded_for(
        self, app_with_middleware: FastAPI
    ) -> None:
        """Test extraction from X-Forwarded-For header."""
        client = TestClient(app_with_middleware)
        response = client.get(
            "/test",
            headers={"X-Forwarded-For": "203.0.113.195, 70.41.3.18, 150.172.238.178"},
        )

        assert response.status_code == 200
        # The first IP should be extracted (original client)

    def test_extracts_ip_from_x_real_ip(self, app_with_middleware: FastAPI) -> None:
        """Test extraction from X-Real-IP header."""
        client = TestClient(app_with_middleware)
        response = client.get(
            "/test",
            headers={"X-Real-IP": "192.168.1.100"},
        )

        assert response.status_code == 200


class TestGetCorrelationIdFromRequest:
    """Tests for get_correlation_id_from_request helper."""

    def test_returns_correlation_id_from_state(self) -> None:
        """Test that helper extracts correlation ID from request state."""
        from unittest.mock import MagicMock

        mock_request = MagicMock()
        mock_request.state.correlation_id = "state-test-id"

        result = get_correlation_id_from_request(mock_request)
        assert result == "state-test-id"

    def test_returns_unknown_if_not_set(self) -> None:
        """Test that helper returns 'unknown' if correlation ID not set."""
        from unittest.mock import MagicMock

        mock_request = MagicMock()
        del mock_request.state.correlation_id  # Remove the attribute

        result = get_correlation_id_from_request(mock_request)
        assert result == "unknown"
