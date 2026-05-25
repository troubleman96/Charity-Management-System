"""
CharityOS — Admin Panel URL Configuration
============================================
Routes for the administrator dashboard and management views.
All routes require 'admin' role (enforced by AdminRequiredMixin).
"""
from django.urls import path
from . import admin_views

app_name = 'admin_panel'

urlpatterns = [
    # Admin dashboard — KPI cards, charts, recent activity
    path('dashboard/', admin_views.AdminDashboardView.as_view(), name='dashboard'),
]
