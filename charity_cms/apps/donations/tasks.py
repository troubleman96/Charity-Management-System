"""
CharityOS — Donations Celery Tasks
=====================================
Background tasks for generating PDF receipts, sending emails,
and periodic low-funds checking.
"""
import os
from celery import shared_task
from django.conf import settings
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils import timezone
import weasyprint


@shared_task(bind=True, max_retries=3)
def send_donation_receipt(self, donation_id):
    """
    Generate a PDF receipt for a donation and email it to the donor.
    Run asynchronously via Celery to avoid blocking the web request.
    """
    from apps.donations.models import Donation, DonationReceipt
    from apps.communications.models import EmailLog

    try:
        donation = Donation.objects.select_related('donor__user', 'receipt').get(id=donation_id)
        receipt = donation.receipt

        # 1. Generate PDF via WeasyPrint
        html_string = render_to_string('donations/receipt_pdf.html', {'donation': donation})
        pdf_file = weasyprint.HTML(string=html_string, base_url=settings.BASE_DIR).write_pdf()

        # 2. Save PDF to disk
        pdf_filename = f'receipts/{receipt.receipt_number}.pdf'
        pdf_path = os.path.join(settings.MEDIA_ROOT, pdf_filename)
        os.makedirs(os.path.dirname(pdf_path), exist_ok=True)

        with open(pdf_path, 'wb') as f:
            f.write(pdf_file)

        receipt.pdf_file = pdf_filename
        receipt.save(update_fields=['pdf_file'])

        # 3. Send Email (if donor has an email)
        if donation.donor and donation.donor.user.email:
            donor_email = donation.donor.user.email

            log = EmailLog.objects.create(
                recipient_email=donor_email,
                subject=f'Donation Receipt - {receipt.receipt_number}',
                email_type='donation_receipt',
                celery_task_id=self.request.id or ''
            )

            try:
                email = EmailMessage(
                    subject=log.subject,
                    body=render_to_string('emails/donation_receipt.html', {'donation': donation}),
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to=[donor_email],
                )
                email.content_subtype = 'html'
                email.attach(f'{receipt.receipt_number}.pdf', pdf_file, 'application/pdf')
                email.send()

                # Update status
                log.status = 'sent'
                log.sent_at = timezone.now()
                receipt.emailed_at = log.sent_at
                receipt.email_status = 'sent'

            except Exception as exc:
                log.status = 'failed'
                log.error_message = str(exc)
                receipt.email_status = 'failed'
                log.save()
                receipt.save()
                # Retry task on failure
                raise self.retry(exc=exc, countdown=60)

            log.save()
            receipt.save(update_fields=['emailed_at', 'email_status'])

    except Donation.DoesNotExist:
        pass


@shared_task
def check_low_funds():
    """
    Periodic task (run hourly via Celery Beat).
    Alerts admins if available cash balance drops below the threshold.
    """
    from apps.donations.models import Donation, DonationAllocation
    from apps.communications.models import Notification
    from django.contrib.auth.models import User
    from django.db.models import Sum

    total_cash = Donation.objects.filter(donation_type='cash').aggregate(
        total=Sum('amount')
    )['total'] or 0

    total_allocated = DonationAllocation.objects.aggregate(
        total=Sum('amount')
    )['total'] or 0

    available = total_cash - total_allocated

    if available < settings.LOW_FUNDS_THRESHOLD:
        admins = User.objects.filter(profile__role='admin')
        for admin in admins:
            Notification.objects.create(
                user=admin,
                notification_type='low_funds',
                title='⚠️ Low Funds Alert',
                message=f'Available funds are TZS {available:,.0f}, below the threshold of TZS {settings.LOW_FUNDS_THRESHOLD:,.0f}.',
                link='/admin-panel/dashboard/'
            )
