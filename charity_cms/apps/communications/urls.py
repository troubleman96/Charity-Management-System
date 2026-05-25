"""
CharityOS — Communications URL Configuration
"""
from django.urls import path
from . import views

app_name = 'communications'

urlpatterns = [
    # Messages
    path('inbox/', views.InboxView.as_view(), name='inbox'),
    path('compose/', views.MessageCreateView.as_view(), name='compose'),
    path('message/<int:pk>/', views.MessageDetailView.as_view(), name='message_detail'),

    # Notifications
    path('notifications/', views.NotificationListView.as_view(), name='notifications'),
    path('notifications/<int:pk>/read/', views.mark_notification_read, name='notification_read'),
    path('notifications/read-all/', views.mark_all_notifications_read, name='notification_read_all'),
]
