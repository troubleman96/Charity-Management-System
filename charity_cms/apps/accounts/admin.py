"""
CharityOS — Accounts Admin Registration
==========================================
Register UserProfile in Django's built-in admin.
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import UserProfile


class UserProfileInline(admin.StackedInline):
    """Inline UserProfile editor within the User admin page."""
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile'
    fields = ('role', 'phone', 'avatar')


class UserAdmin(BaseUserAdmin):
    """Extended User admin with inline profile editing."""
    inlines = (UserProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'get_role', 'is_active')
    list_filter = ('is_active', 'profile__role')

    def get_role(self, obj):
        """Display the user's role in the list view."""
        return obj.profile.get_role_display() if hasattr(obj, 'profile') else '-'
    get_role.short_description = 'Role'


# Re-register User with our custom admin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
