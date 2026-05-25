"""
CharityOS — Custom Authentication Backend
=============================================
Allows users to log in with their email address instead of username.
Django's default AuthenticationForm sends the field as 'username',
so this backend checks if the input is an email and looks up the User by email.
"""
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User


class EmailOrUsernameBackend(ModelBackend):
    """
    Authenticate against either username or email.
    Django tries each backend in AUTHENTICATION_BACKENDS until one succeeds.
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        # First, try to find user by email (covers most login attempts)
        try:
            user = User.objects.get(email=username)
        except User.DoesNotExist:
            # Fall back to username lookup
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                return None

        # Check the password and ensure the user is active
        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None
