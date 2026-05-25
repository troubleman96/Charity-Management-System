"""
CharityOS — Donors URL Configuration
"""
from django.urls import path
from . import views

app_name = 'donors'

urlpatterns = [
    path('dashboard/', views.DonorDashboardView.as_view(), name='dashboard'),
    path('history/', views.DonationHistoryView.as_view(), name='history'),
]
