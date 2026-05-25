import os
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.development")
django.setup()

from apps.accounts.backends import EmailOrUsernameBackend

backend = EmailOrUsernameBackend()
user = backend.authenticate(None, username="admin@gmail.com", password="admin123")
print(f"Authenticated user: {user}")

