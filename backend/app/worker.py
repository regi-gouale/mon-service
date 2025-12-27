"""
Celery Worker Configuration.

This module configures the Celery worker for background task processing.
"""

from typing import Any

from celery import Celery

from app.core.config import settings

# Create Celery app
celery_app = Celery(
    "church_team_management",
    broker=str(settings.redis_url),
    backend=str(settings.redis_url),
)

# Celery configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    worker_prefetch_multiplier=1,
    task_acks_late=True,
    task_reject_on_worker_lost=True,
)

# Auto-discover tasks from the workers.tasks module
celery_app.autodiscover_tasks(["app.workers.tasks"])


@celery_app.task(bind=True)  # type: ignore[misc]
def debug_task(self: Any) -> str:
    """Debug task for testing Celery connection."""
    print(f"Request: {self.request!r}")
    return "pong"
