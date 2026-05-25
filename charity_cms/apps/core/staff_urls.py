"""
CharityOS — Staff Panel URL Configuration
============================================
Routes for the staff dashboard and management views.
All routes require 'staff' or 'admin' role (enforced by StaffRequiredMixin).
"""
from django.urls import path
from . import staff_views

app_name = 'staff_panel'

urlpatterns = [
    # Staff dashboard — beneficiary overview, pending tasks
    path('dashboard/', staff_views.StaffDashboardView.as_view(), name='dashboard'),
]
