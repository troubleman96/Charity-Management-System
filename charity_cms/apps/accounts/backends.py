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
        print(f"DEBUG: Authenticating username/email: '{username}' with password: '{password}'")
        # First, try to find user by email (covers most login attempts)
        try:
            user = User.objects.get(email=username)
            print(f"DEBUG: Found user by email: {user}")
        except User.DoesNotExist:
            print(f"DEBUG: User not found by email, trying username")
            # Fall back to username lookup
            try:
                user = User.objects.get(username=username)
                print(f"DEBUG: Found user by username: {user}")
            except User.DoesNotExist:
                print("DEBUG: User not found by email or username")
                return None

        # Check the password and ensure the user is active
        if user.check_password(password):
            print("DEBUG: Password matched")
            if self.user_can_authenticate(user):
                print("DEBUG: User can authenticate")
                return user
            else:
                print("DEBUG: user_can_authenticate returned False")
        else:
            print("DEBUG: Password did not match")
        return None
