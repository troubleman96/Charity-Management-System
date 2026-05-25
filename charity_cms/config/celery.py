"""
CharityOS — Celery Configuration
Configures the Celery task queue with Redis as the message broker.
Auto-discovers tasks from all installed Django apps.
"""
import os
from celery import Celery

# Use development settings by default
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')

# Create the Celery application instance
app = Celery('charity_cms')

# Load config from Django settings, using the CELERY_ namespace
# e.g., CELERY_BROKER_URL in settings becomes broker_url in Celery
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-discover tasks.py in all installed apps
app.autodiscover_tasks()


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    """Debug task for testing Celery connectivity."""
    print(f'Request: {self.request!r}')
