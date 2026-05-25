"""
CharityOS config package initializer.
Ensures Celery app is loaded when Django starts, so that
@shared_task decorators use the correct Celery app instance.
"""
from .celery import app as celery_app

__all__ = ('celery_app',)
