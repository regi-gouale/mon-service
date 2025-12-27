"""
Email Tasks.

Celery tasks for asynchronous email sending.
These tasks allow emails to be sent in the background without
blocking the main request thread.

Usage:
    from app.workers.tasks.email_tasks import send_verification_email_task

    # Queue email for async sending
    send_verification_email_task.delay(
        email="user@example.com",
        user_name="John Doe",
        verification_token="abc123"
    )
"""

import asyncio
import logging
from typing import Any

from celery import shared_task

from app.services.email_service import email_service

logger = logging.getLogger(__name__)


def _run_async(coro: Any) -> Any:
    """Run an async coroutine in a sync context."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


@shared_task(
    name="email.send_verification",
    bind=True,
    max_retries=3,
    default_retry_delay=60,
)
def send_verification_email_task(
    self: Any,
    email: str,
    user_name: str,
    verification_token: str,
    expiration_hours: int = 24,
) -> bool:
    """
    Celery task to send verification email asynchronously.

    Args:
        email: User's email address
        user_name: User's display name
        verification_token: Token for email verification
        expiration_hours: Hours until token expires

    Returns:
        True if email was sent successfully
    """
    try:
        logger.info(f"Sending verification email to {email}")
        result = _run_async(
            email_service.send_verification_email(
                email=email,
                user_name=user_name,
                verification_token=verification_token,
                expiration_hours=expiration_hours,
            )
        )
        if result:
            logger.info(f"Verification email sent successfully to {email}")
        else:
            logger.warning(f"Failed to send verification email to {email}")
        return bool(result)
    except Exception as exc:
        logger.error(f"Error sending verification email to {email}: {exc}")
        raise self.retry(exc=exc)


@shared_task(
    name="email.send_password_reset",
    bind=True,
    max_retries=3,
    default_retry_delay=60,
)
def send_password_reset_email_task(
    self: Any,
    email: str,
    user_name: str,
    reset_token: str,
    expiration_hours: int = 1,
) -> bool:
    """
    Celery task to send password reset email asynchronously.

    Args:
        email: User's email address
        user_name: User's display name
        reset_token: Token for password reset
        expiration_hours: Hours until token expires

    Returns:
        True if email was sent successfully
    """
    try:
        logger.info(f"Sending password reset email to {email}")
        result = _run_async(
            email_service.send_password_reset_email(
                email=email,
                user_name=user_name,
                reset_token=reset_token,
                expiration_hours=expiration_hours,
            )
        )
        if result:
            logger.info(f"Password reset email sent successfully to {email}")
        else:
            logger.warning(f"Failed to send password reset email to {email}")
        return bool(result)
    except Exception as exc:
        logger.error(f"Error sending password reset email to {email}: {exc}")
        raise self.retry(exc=exc)


@shared_task(
    name="email.send_invitation",
    bind=True,
    max_retries=3,
    default_retry_delay=60,
)
def send_invitation_email_task(
    self: Any,
    email: str,
    user_name: str,
    organization_name: str,
    department_name: str,
    invitation_token: str,
    expiration_days: int = 7,
) -> bool:
    """
    Celery task to send team invitation email asynchronously.

    Args:
        email: Invitee's email address
        user_name: Invitee's name or email
        organization_name: Name of the organization
        department_name: Name of the department/team
        invitation_token: Token for accepting invitation
        expiration_days: Days until invitation expires

    Returns:
        True if email was sent successfully
    """
    try:
        logger.info(f"Sending invitation email to {email}")
        result = _run_async(
            email_service.send_invitation_email(
                email=email,
                user_name=user_name,
                organization_name=organization_name,
                department_name=department_name,
                invitation_token=invitation_token,
                expiration_days=expiration_days,
            )
        )
        if result:
            logger.info(f"Invitation email sent successfully to {email}")
        else:
            logger.warning(f"Failed to send invitation email to {email}")
        return bool(result)
    except Exception as exc:
        logger.error(f"Error sending invitation email to {email}: {exc}")
        raise self.retry(exc=exc)


@shared_task(
    name="email.send_generic",
    bind=True,
    max_retries=3,
    default_retry_delay=60,
)
def send_generic_email_task(
    self: Any,
    recipients: list[str],
    subject: str,
    body: str,
) -> bool:
    """
    Celery task to send a generic email asynchronously.

    Args:
        recipients: List of email addresses
        subject: Email subject
        body: Email body (HTML)

    Returns:
        True if email was sent successfully
    """
    try:
        logger.info(f"Sending generic email to {recipients}")
        result = _run_async(
            email_service.send_email(
                recipients=recipients,
                subject=subject,
                body=body,
            )
        )
        if result:
            logger.info(f"Generic email sent successfully to {recipients}")
        else:
            logger.warning(f"Failed to send generic email to {recipients}")
        return bool(result)
    except Exception as exc:
        logger.error(f"Error sending generic email to {recipients}: {exc}")
        raise self.retry(exc=exc)
