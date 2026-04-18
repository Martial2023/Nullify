"""Celery application — broker & backend on Redis."""

from celery import Celery

from app.config import settings

celery = Celery(
    "nullify",
    broker=settings.redis_url,
    backend=settings.redis_url,
)

celery.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    task_track_started=True,
    result_expires=3600,  # results expire after 1h
    task_acks_late=True,
    worker_prefetch_multiplier=1,  # one task at a time per worker
)

# Auto-discover tasks in app.tasks
celery.autodiscover_tasks(["app"])
