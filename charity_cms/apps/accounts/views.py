"""
CharityOS — Accounts Views
=============================
Authentication views: login, logout, register, and profile management.
"""
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import DonorRegistrationForm, LoginForm, ProfileUpdateForm
from apps.core.utils import log_action


def login_view(request):
    """
    Handle user login with email/password.
    Redirects to role-specific dashboard on success.
    Logs all login attempts (success and failure) per FR-1.6.
    """
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)

            # Log successful login
            log_action(user, 'auth.login', description='Successful login', request=request)

            messages.success(request, f'Welcome back, {user.get_full_name() or user.username}!')
            return redirect('dashboard')
        else:
            # Log failed login attempt
            username = request.POST.get('username', 'unknown')
            log_action(
                None, 'auth.login_failed',
                description=f'Failed login attempt for: {username}',
                request=request
            )
            messages.error(request, 'Invalid email or password.')
    else:
        form = LoginForm()

    return render(request, 'accounts/login.html', {'form': form})


def register_view(request):
    """
    Public donor registration form.
    Creates a User + UserProfile (donor role) + Donor model.
    """
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = DonorRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()

            # Update profile phone number
            if form.cleaned_data.get('phone'):
                user.profile.phone = form.cleaned_data['phone']
                user.profile.save()

            # Create the Donor record
            from apps.donors.models import Donor
            Donor.objects.create(user=user)

            # Log the registration
            log_action(user, 'auth.register', description='New donor registration', request=request)

            # Auto-login after registration
            login(request, user)
            messages.success(request, 'Welcome! Your donor account has been created.')
            return redirect('dashboard')
    else:
        form = DonorRegistrationForm()

    return render(request, 'accounts/register.html', {'form': form})


def logout_view(request):
    """
    Log the user out and redirect to landing page.
    """
    if request.user.is_authenticated:
        log_action(request.user, 'auth.logout', description='User logged out', request=request)
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('landing')


@login_required
def profile_view(request):
    """
    User profile page — view and update personal information.
    """
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()

            # Update phone number on profile
            phone = form.cleaned_data.get('phone')
            if phone is not None:
                request.user.profile.phone = phone
                request.user.profile.save()

            log_action(
                request.user, 'profile.updated',
                description='Profile information updated',
                request=request
            )
            messages.success(request, 'Profile updated successfully.')
            return redirect('accounts:profile')
    else:
        form = ProfileUpdateForm(
            instance=request.user,
            initial={'phone': request.user.profile.phone if hasattr(request.user, 'profile') else ''}
        )

    return render(request, 'accounts/profile.html', {'form': form})
