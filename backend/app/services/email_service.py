"""
Email Service.

This module provides email sending functionality using FastAPI-Mail.
Supports both synchronous and asynchronous (via Celery) email sending.

Usage:
    from app.services.email_service import email_service

    # Send verification email
    await email_service.send_verification_email(
        email="user@example.com",
        user_name="John Doe",
        verification_token="abc123"
    )
"""

import logging
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType
from jinja2 import Environment, FileSystemLoader, select_autoescape
from pydantic import EmailStr

from app.core.config import settings

logger = logging.getLogger(__name__)


def _get_email_config() -> ConnectionConfig:
    """Create FastAPI-Mail configuration from settings."""
    return ConnectionConfig(
        MAIL_USERNAME=settings.smtp_user or "",
        MAIL_PASSWORD=settings.smtp_password or "",
        MAIL_FROM=settings.smtp_from_email,
        MAIL_PORT=settings.smtp_port,
        MAIL_SERVER=settings.smtp_host,
        MAIL_FROM_NAME=settings.smtp_from_name,
        MAIL_STARTTLS=settings.smtp_tls,
        MAIL_SSL_TLS=settings.smtp_ssl,
        USE_CREDENTIALS=bool(settings.smtp_user and settings.smtp_password),
        VALIDATE_CERTS=settings.app_env == "production",
    )


class EmailService:
    """
    Service for sending transactional emails.

    Provides methods for common email types:
    - Email verification
    - Password reset
    - Invitations
    - Notifications
    """

    def __init__(self) -> None:
        """Initialize the email service with configuration and templates."""
        self._config = _get_email_config()
        self._mailer = FastMail(self._config)

        # Set up Jinja2 template environment
        templates_path = Path(__file__).parent.parent / "templates"
        self._jinja_env = Environment(
            loader=FileSystemLoader(str(templates_path)),
            autoescape=select_autoescape(["html", "xml"]),
        )

    def _get_base_context(self) -> dict[str, Any]:
        """Get base template context with common variables."""
        return {
            "app_name": settings.app_name,
            "current_year": datetime.now(UTC).year,
        }

    def _render_template(self, template_name: str, **context: Any) -> str:
        """
        Render an email template with the given context.

        Args:
            template_name: Name of the template file (e.g., "email/verification.html")
            **context: Template context variables

        Returns:
            Rendered HTML string
        """
        template = self._jinja_env.get_template(template_name)
        full_context = {**self._get_base_context(), **context}
        return str(template.render(**full_context))

    async def send_email(
        self,
        recipients: list[EmailStr],
        subject: str,
        body: str,
        subtype: MessageType = MessageType.html,
    ) -> bool:
        """
        Send an email to one or more recipients.

        Args:
            recipients: List of email addresses
            subject: Email subject
            body: Email body (HTML or plain text)
            subtype: Message type (html or plain)

        Returns:
            True if email was sent successfully, False otherwise
        """
        try:
            message = MessageSchema(
                subject=subject,
                recipients=recipients,
                body=body,
                subtype=subtype,
            )
            await self._mailer.send_message(message)
            logger.info(f"Email sent successfully to {recipients}")
            return True
        except Exception as e:
            logger.error(f"Failed to send email to {recipients}: {e}")
            return False

    async def send_verification_email(
        self,
        email: EmailStr,
        user_name: str,
        verification_token: str,
        expiration_hours: int = 24,
    ) -> bool:
        """
        Send email verification email to a new user.

        Args:
            email: User's email address
            user_name: User's display name
            verification_token: Token for email verification
            expiration_hours: Hours until token expires

        Returns:
            True if email was sent successfully
        """
        # Build verification URL
        frontend_url = (
            settings.cors_origins[0]
            if settings.cors_origins
            else "http://localhost:3000"
        )
        verification_url = (
            f"{frontend_url}/auth/verify-email?token={verification_token}"
        )

        body = self._render_template(
            "email/email_verification.html",
            subject="Vérification de votre email",
            user_name=user_name,
            verification_url=verification_url,
            expiration_hours=expiration_hours,
        )

        return await self.send_email(
            recipients=[email],
            subject=f"Vérifiez votre email - {settings.app_name}",
            body=body,
        )

    async def send_password_reset_email(
        self,
        email: EmailStr,
        user_name: str,
        reset_token: str,
        expiration_hours: int = 1,
    ) -> bool:
        """
        Send password reset email.

        Args:
            email: User's email address
            user_name: User's display name
            reset_token: Token for password reset
            expiration_hours: Hours until token expires

        Returns:
            True if email was sent successfully
        """
        frontend_url = (
            settings.cors_origins[0]
            if settings.cors_origins
            else "http://localhost:3000"
        )
        reset_url = f"{frontend_url}/auth/reset-password?token={reset_token}"

        body = self._render_template(
            "email/password_reset.html",
            subject="Réinitialisation de votre mot de passe",
            user_name=user_name,
            reset_url=reset_url,
            expiration_hours=expiration_hours,
        )

        return await self.send_email(
            recipients=[email],
            subject=f"Réinitialisation de mot de passe - {settings.app_name}",
            body=body,
        )

    async def send_invitation_email(
        self,
        email: EmailStr,
        user_name: str,
        organization_name: str,
        department_name: str,
        invitation_token: str,
        expiration_days: int = 7,
    ) -> bool:
        """
        Send team invitation email.

        Args:
            email: Invitee's email address
            user_name: Invitee's name (if known) or email
            organization_name: Name of the organization
            department_name: Name of the department/team
            invitation_token: Token for accepting invitation
            expiration_days: Days until invitation expires

        Returns:
            True if email was sent successfully
        """
        frontend_url = (
            settings.cors_origins[0]
            if settings.cors_origins
            else "http://localhost:3000"
        )
        invitation_url = (
            f"{frontend_url}/auth/accept-invitation?token={invitation_token}"
        )

        body = self._render_template(
            "email/invitation.html",
            subject="Invitation à rejoindre une équipe",
            user_name=user_name,
            organization_name=organization_name,
            department_name=department_name,
            invitation_url=invitation_url,
            expiration_days=expiration_days,
        )

        return await self.send_email(
            recipients=[email],
            subject=f"Vous êtes invité(e) à rejoindre {organization_name} - {settings.app_name}",
            body=body,
        )


# Global email service instance
email_service = EmailService()
