"""
CharityOS — Donations URL Configuration
"""
from django.urls import path
from . import views

app_name = 'donations'

urlpatterns = [
    path('', views.DonationListView.as_view(), name='list'),
    path('create/', views.DonationCreateView.as_view(), name='create'),
    path('<int:pk>/', views.DonationDetailView.as_view(), name='detail'),
    path('<int:pk>/allocate/', views.AllocationCreateView.as_view(), name='allocate'),
]
