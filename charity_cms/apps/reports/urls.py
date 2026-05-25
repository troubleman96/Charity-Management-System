"""
CharityOS — Reports URL Configuration
"""
from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    path('', views.ReportIndexView.as_view(), name='index'),
    path('monthly/', views.MonthlySummaryReportView.as_view(), name='monthly_summary'),
    path('donors/', views.DonorReportView.as_view(), name='donor_report'),
]
