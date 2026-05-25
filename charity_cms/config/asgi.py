"""
CharityOS — ASGI Configuration
Exposes the ASGI callable for async-capable servers (e.g., Daphne, Uvicorn).
"""
import os
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')

application = get_asgi_application()
