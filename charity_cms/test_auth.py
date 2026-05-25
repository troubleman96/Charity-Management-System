import os
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.development")
django.setup()

from django.contrib.auth import authenticate
from django.contrib.auth.models import User

# Check user exists
u = User.objects.get(username="admin")
print(f"User: {u.username}, Email: {u.email}, is_active: {u.is_active}")

# Test auth with known credentials, wait we don't know the password
print("Auth backends:", [b.__class__.__name__ for b in django.contrib.auth.get_backends()])

