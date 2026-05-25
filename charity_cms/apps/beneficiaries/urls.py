"""
CharityOS — Beneficiaries URL Configuration
"""
from django.urls import path
from . import views

app_name = 'beneficiaries'

urlpatterns = [
    # Beneficiary CRUD
    path('', views.BeneficiaryListView.as_view(), name='list'),
    path('create/', views.BeneficiaryCreateView.as_view(), name='create'),
    path('<int:pk>/', views.BeneficiaryDetailView.as_view(), name='detail'),
    path('<int:pk>/edit/', views.BeneficiaryUpdateView.as_view(), name='edit'),

    # Assistance Requests
    path('requests/', views.AssistanceRequestListView.as_view(), name='requests'),
    path('requests/create/', views.AssistanceRequestCreateView.as_view(), name='request_create'),
    path('requests/<int:pk>/review/', views.review_request, name='request_review'),

    # Progress Updates
    path('updates/create/', views.BeneficiaryProgressCreateView.as_view(), name='update_create'),
]
