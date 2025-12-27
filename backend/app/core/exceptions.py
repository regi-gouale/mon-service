"""
Application Exceptions.

This module contains custom exception classes and exception handlers
for the application.
"""

from typing import Any

from fastapi import HTTPException, status


class AppException(Exception):
    """Base exception for the application."""

    def __init__(
        self,
        message: str = "An error occurred",
        details: dict[str, Any] | None = None,
    ) -> None:
        self.message = message
        self.details = details or {}
        super().__init__(self.message)


class NotFoundError(AppException):
    """Exception raised when a resource is not found."""

    def __init__(
        self,
        resource: str = "Resource",
        resource_id: str | int | None = None,
    ) -> None:
        message = f"{resource} not found"
        if resource_id:
            message = f"{resource} with ID '{resource_id}' not found"
        super().__init__(message=message)


class AlreadyExistsError(AppException):
    """Exception raised when a resource already exists."""

    def __init__(
        self,
        resource: str = "Resource",
        field: str | None = None,
        value: str | None = None,
    ) -> None:
        message = f"{resource} already exists"
        if field and value:
            message = f"{resource} with {field} '{value}' already exists"
        super().__init__(message=message)


class UnauthorizedError(AppException):
    """Exception raised when authentication fails."""

    def __init__(self, message: str = "Authentication required") -> None:
        super().__init__(message=message)


class ForbiddenError(AppException):
    """Exception raised when access is denied."""

    def __init__(self, message: str = "Access denied") -> None:
        super().__init__(message=message)


class ValidationError(AppException):
    """Exception raised when validation fails."""

    def __init__(
        self,
        message: str = "Validation error",
        errors: list[dict[str, Any]] | None = None,
    ) -> None:
        super().__init__(message=message, details={"errors": errors or []})


class BusinessRuleError(AppException):
    """Exception raised when a business rule is violated."""

    def __init__(
        self,
        message: str = "Business rule violation",
        rule: str | None = None,
    ) -> None:
        details = {"rule": rule} if rule else {}
        super().__init__(message=message, details=details)


class ConflictError(AppException):
    """Exception raised when there is a conflict (e.g., resource already exists)."""

    def __init__(
        self,
        message: str = "Resource conflict",
    ) -> None:
        super().__init__(message=message)


class PermissionDeniedError(AppException):
    """Exception raised when user lacks permission for an action."""

    def __init__(
        self,
        message: str = "Permission denied",
    ) -> None:
        super().__init__(message=message)


# HTTP Exception factories for FastAPI


def not_found_exception(
    resource: str = "Resource",
    resource_id: str | int | None = None,
) -> HTTPException:
    """Create a 404 Not Found HTTP exception."""
    detail = f"{resource} not found"
    if resource_id:
        detail = f"{resource} with ID '{resource_id}' not found"
    return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


def unauthorized_exception(
    detail: str = "Authentication required",
) -> HTTPException:
    """Create a 401 Unauthorized HTTP exception."""
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=detail,
        headers={"WWW-Authenticate": "Bearer"},
    )


def forbidden_exception(
    detail: str = "Access denied",
) -> HTTPException:
    """Create a 403 Forbidden HTTP exception."""
    return HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=detail)


def bad_request_exception(
    detail: str = "Bad request",
) -> HTTPException:
    """Create a 400 Bad Request HTTP exception."""
    return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)


def conflict_exception(
    detail: str = "Resource already exists",
) -> HTTPException:
    """Create a 409 Conflict HTTP exception."""
    return HTTPException(status_code=status.HTTP_409_CONFLICT, detail=detail)
