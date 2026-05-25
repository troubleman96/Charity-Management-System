"""
CharityOS — Communications Views
===================================
Views for managing the inbox, sending messages, and viewing notifications.
"""
from django.views.generic import ListView, CreateView, DetailView, FormView
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse_lazy
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from apps.core.mixins import RoleRequiredMixin, AdminRequiredMixin
from apps.core.utils import log_action
from .models import Message, Notification
from .forms import MessageForm, BroadcastForm


class InboxView(RoleRequiredMixin, ListView):
    """
    User's internal message inbox.
    Available to admins and staff.
    """
    allowed_roles = ['admin', 'staff']
    model = Message
    template_name = 'communications/inbox.html'
    context_object_name = 'messages'
    paginate_by = 20

    def get_queryset(self):
        return Message.objects.filter(recipient=self.request.user).select_related('sender')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['sent_messages'] = Message.objects.filter(sender=self.request.user).select_related('recipient')[:5]
        return ctx


class MessageDetailView(RoleRequiredMixin, DetailView):
    """
    Read a specific message. Marks it as read upon viewing.
    """
    allowed_roles = ['admin', 'staff']
    model = Message
    template_name = 'communications/message_detail.html'
    context_object_name = 'msg'

    def get_queryset(self):
        # Users can only read messages sent to or from them
        return Message.objects.filter(
            models.Q(recipient=self.request.user) | models.Q(sender=self.request.user)
        )

    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        msg = self.object
        if msg.recipient == request.user and not msg.is_read:
            msg.is_read = True
            msg.read_at = timezone.now()
            msg.save(update_fields=['is_read', 'read_at'])
        return response


class MessageCreateView(RoleRequiredMixin, SuccessMessageMixin, CreateView):
    """
    Compose and send a new internal message.
    """
    allowed_roles = ['admin', 'staff']
    model = Message
    form_class = MessageForm
    template_name = 'communications/compose.html'
    success_url = reverse_lazy('communications:inbox')
    success_message = 'Message sent successfully.'

    def form_valid(self, form):
        form.instance.sender = self.request.user
        response = super().form_valid(form)
        log_action(self.request.user, 'message.sent', self.object, 'Sent internal message', self.request)
        return response


class NotificationListView(ListView):
    """
    List of system notifications for the current user.
    """
    model = Notification
    template_name = 'communications/notifications.html'
    context_object_name = 'notifications'
    paginate_by = 30

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)


@login_required
def mark_notification_read(request, pk):
    """
    Mark a specific notification as read and redirect to its link (if any).
    """
    notif = get_object_or_404(Notification, pk=pk, user=request.user)
    if not notif.is_read:
        notif.is_read = True
        notif.save(update_fields=['is_read'])

    if notif.link:
        return redirect(notif.link)
    return redirect('communications:notifications')


@login_required
def mark_all_notifications_read(request):
    """Mark all unread notifications as read via HTMX or standard request."""
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)

    if request.headers.get('HX-Request'):
        # If HTMX, we can just return a 200 OK or empty response
        from django.http import HttpResponse
        return HttpResponse('')
    return redirect('communications:notifications')
