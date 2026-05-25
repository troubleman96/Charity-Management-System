import os
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.development")
django.setup()

from apps.accounts.forms import LoginForm
from django.http import HttpRequest

request = HttpRequest()
form = LoginForm(request, data={'username': 'admin@gmail.com', 'password': 'admin123'})
is_valid = form.is_valid()
print(f"Is valid? {is_valid}")
if not is_valid:
    print(f"Errors: {form.errors}")

