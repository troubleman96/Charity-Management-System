"""
CharityOS — Accounts Signals
================================
Auto-create a UserProfile whenever a new User is created.
This ensures every User always has an associated profile.
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import UserProfile


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Signal handler: Create a UserProfile when a new User is created.
    Default role is 'donor' (most common registration type).
    """
    if created:
        role = 'admin' if instance.is_superuser else 'donor'
        UserProfile.objects.create(user=instance, role=role)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """
    Signal handler: Save the UserProfile whenever the User is saved.
    Ensures profile data stays in sync with User data.
    """
    if hasattr(instance, 'profile'):
        instance.profile.save()
