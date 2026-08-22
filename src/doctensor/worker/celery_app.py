"""Celery application factory."""
from celery import Celery


def make_celery(redis_url: str = "redis://localhost:6379/0") -> Celery:
    app = Celery(
        "doctensor",
        broker=redis_url,
        backend=redis_url,
        include=["doctensor.worker.tasks"],
    )
    app.conf.update(
        task_serializer="json",
        result_serializer="json",
        accept_content=["json"],
        timezone="UTC",
        enable_utc=True,
        task_track_started=True,
        result_expires=86400,  # 24 hours
    )
    return app


# Module-level instance (used by tasks.py and CLI)
def get_celery_app() -> Celery:
    from doctensor.api.config import get_settings
    return make_celery(get_settings().redis_url)
