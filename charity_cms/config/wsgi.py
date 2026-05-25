"""
CharityOS — WSGI Configuration
Exposes the WSGI callable as a module-level variable named ``application``.
Used by Gunicorn and other WSGI servers in production.
"""
import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')

application = get_wsgi_application()
