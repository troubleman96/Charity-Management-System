"""
CharityOS — Core URL Configuration
=====================================
Public routes: landing page and dashboard redirect.
"""
from django.urls import path
from . import views

urlpatterns = [
    # Public landing page
    path('', views.LandingPageView.as_view(), name='landing'),

    # Role-based dashboard redirect (requires login)
    path('dashboard/', views.dashboard_redirect, name='dashboard'),
]
