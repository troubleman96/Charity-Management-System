# Django Build Guide
## Charity Management System — Full Stack
---

## 1. Project Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Install dependencies
pip install django==5.1 \
    psycopg2-binary \
    djangorestframework \
    celery \
    redis \
    django-environ \
    Pillow \
    WeasyPrint \
    django-crispy-forms \
    crispy-tailwind \
    django-htmx \
    whitenoise \
    gunicorn \
    django-storages \
    boto3 \
    africastalking

# Create project
django-admin startproject config .

# Create apps
python manage.py startapp accounts
python manage.py startapp donors
python manage.py startapp beneficiaries
python manage.py startapp donations
python manage.py startapp communications
python manage.py startapp core
python manage.py startapp reports
```

---

## 2. Project Structure

```
charity_cms/
├── config/
│   ├── __init__.py
│   ├── settings/
│   │   ├── base.py
│   │   ├── development.py
│   │   └── production.py
│   ├── urls.py
│   ├── celery.py
│   └── wsgi.py
│
├── apps/
│   ├── accounts/          # Auth, UserProfile, RBAC
│   ├── donors/            # Donor model, donor dashboard
│   ├── beneficiaries/     # Beneficiary, AssistanceRequest, Updates
│   ├── donations/         # Donation, Receipt, Allocation
│   ├── communications/    # Message, Notification, EmailLog
│   ├── reports/           # PDF generation, report views
│   └── core/              # AuditLog, base templates, mixins
│
├── templates/
│   ├── base.html
│   ├── landing/
│   ├── accounts/
│   ├── admin_panel/
│   ├── donor_portal/
│   ├── beneficiaries/
│   ├── donations/
│   └── communications/
│
├── static/
│   ├── css/
│   ├── js/
│   └── images/
│
├── media/              # User uploads (photos, PDFs)
├── .env
├── manage.py
├── requirements.txt
├── docker-compose.yml
└── Dockerfile
```

---

## 3. Settings (config/settings/base.py)

```python
from pathlib import Path
import environ

env = environ.Env()
environ.Env.read_env()

BASE_DIR = Path(__file__).resolve().parent.parent.parent

SECRET_KEY = env('SECRET_KEY')
DEBUG = env.bool('DEBUG', default=False)
ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=[])

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Third party
    'crispy_forms',
    'crispy_tailwind',
    'django_htmx',
    'rest_framework',
    # Local apps
    'apps.accounts',
    'apps.donors',
    'apps.beneficiaries',
    'apps.donations',
    'apps.communications',
    'apps.reports',
    'apps.core',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django_htmx.middleware.HtmxMiddleware',
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': env('DB_NAME'),
        'USER': env('DB_USER'),
        'PASSWORD': env('DB_PASSWORD'),
        'HOST': env('DB_HOST', default='localhost'),
        'PORT': env('DB_PORT', default='5432'),
    }
}

# Celery
CELERY_BROKER_URL = env('REDIS_URL', default='redis://localhost:6379/0')
CELERY_RESULT_BACKEND = env('REDIS_URL', default='redis://localhost:6379/0')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'

# Email
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = env('EMAIL_HOST')
EMAIL_PORT = env.int('EMAIL_PORT', default=587)
EMAIL_USE_TLS = True
EMAIL_HOST_USER = env('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = env('DEFAULT_FROM_EMAIL', default='noreply@charity.org')

# Auth
LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/dashboard/'
LOGOUT_REDIRECT_URL = '/'
SESSION_COOKIE_AGE = 1800  # 30 minutes

# Crispy
CRISPY_ALLOWED_TEMPLATE_PACKS = 'tailwind'
CRISPY_TEMPLATE_PACK = 'tailwind'

# Media
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Static
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Charity-specific settings
LOW_FUNDS_THRESHOLD = env.float('LOW_FUNDS_THRESHOLD', default=100000.00)  # TZS
ORGANIZATION_NAME = env('ORG_NAME', default='Orphan Support Group')
ORGANIZATION_LOGO = 'images/org_logo.png'
```

---

## 4. Models

### accounts/models.py
```python
from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('admin', 'Administrator'),
        ('staff', 'Staff/Volunteer'),
        ('donor', 'Donor'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    phone = models.CharField(max_length=20, blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.get_full_name()} ({self.role})"

    class Meta:
        indexes = [models.Index(fields=['role'])]
```

### donors/models.py
```python
from django.db import models
from django.contrib.auth.models import User

class Donor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='donor_profile')
    organization = models.CharField(max_length=200, blank=True)
    address = models.TextField(blank=True)
    national_id = models.CharField(max_length=50, blank=True)
    is_anonymous = models.BooleanField(default=False)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.get_full_name() or self.user.email

    @property
    def total_donated(self):
        return self.donations.filter(donation_type='cash').aggregate(
            total=models.Sum('amount'))['total'] or 0
```

### beneficiaries/models.py
```python
from django.db import models
from django.contrib.auth.models import User
from apps.donors.models import Donor

class Beneficiary(models.Model):
    STATUS_CHOICES = [('active', 'Active'), ('inactive', 'Inactive'), ('graduated', 'Graduated')]
    GENDER_CHOICES = [('male', 'Male'), ('female', 'Female')]

    beneficiary_code = models.CharField(max_length=20, unique=True, editable=False)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    photo = models.ImageField(upload_to='beneficiaries/', blank=True, null=True)
    school_name = models.CharField(max_length=200, blank=True)
    school_grade = models.CharField(max_length=50, blank=True)
    health_status = models.TextField(blank=True)
    guardian_name = models.CharField(max_length=200, blank=True)
    guardian_phone = models.CharField(max_length=20, blank=True)
    guardian_relationship = models.CharField(max_length=50, blank=True)
    location_region = models.CharField(max_length=100, blank=True)
    location_district = models.CharField(max_length=100, blank=True)
    date_enrolled = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    notes = models.TextField(blank=True)
    registered_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.beneficiary_code:
            from datetime import date
            year = date.today().year
            last = Beneficiary.objects.filter(
                beneficiary_code__startswith=f'BEN-{year}').count()
            self.beneficiary_code = f'BEN-{year}-{str(last+1).zfill(4)}'
        super().save(*args, **kwargs)

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def age(self):
        from datetime import date
        today = date.today()
        return today.year - self.date_of_birth.year - (
            (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day))

    class Meta:
        verbose_name_plural = 'Beneficiaries'
        ordering = ['-date_enrolled']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['beneficiary_code']),
        ]


class DonorBeneficiaryLink(models.Model):
    donor = models.ForeignKey(Donor, on_delete=models.CASCADE, related_name='sponsored_beneficiaries')
    beneficiary = models.ForeignKey(Beneficiary, on_delete=models.CASCADE, related_name='donors')
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    notes = models.TextField(blank=True)

    class Meta:
        unique_together = ('donor', 'beneficiary')


class AssistanceRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('fulfilled', 'Fulfilled'),
    ]
    REQUEST_TYPES = [
        ('education', 'Education'),
        ('food', 'Food'),
        ('medical', 'Medical'),
        ('clothing', 'Clothing'),
        ('other', 'Other'),
    ]

    request_ref = models.CharField(max_length=30, unique=True, editable=False)
    beneficiary = models.ForeignKey(Beneficiary, on_delete=models.CASCADE, related_name='requests')
    requested_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='submitted_requests')
    request_type = models.CharField(max_length=50, choices=REQUEST_TYPES)
    description = models.TextField()
    estimated_cost = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviewed_requests')
    review_notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.request_ref:
            from datetime import date
            year = date.today().year
            last = AssistanceRequest.objects.filter(
                request_ref__startswith=f'REQ-{year}').count()
            self.request_ref = f'REQ-{year}-{str(last+1).zfill(4)}'
        super().save(*args, **kwargs)
```

### donations/models.py
```python
from django.db import models
from django.contrib.auth.models import User
from apps.donors.models import Donor
from apps.beneficiaries.models import Beneficiary, AssistanceRequest

class Donation(models.Model):
    DONATION_TYPES = [('cash', 'Cash'), ('in_kind', 'In-Kind')]
    STATUS_CHOICES = [('received', 'Received'), ('allocated', 'Fully Allocated'), ('partial', 'Partially Allocated')]
    PAYMENT_METHODS = [
        ('cash', 'Cash'), ('mpesa', 'M-Pesa'),
        ('tigopesa', 'Tigo Pesa'), ('bank', 'Bank Transfer'), ('other', 'Other'),
    ]

    donation_ref = models.CharField(max_length=30, unique=True, editable=False)
    donor = models.ForeignKey(Donor, on_delete=models.SET_NULL, null=True, blank=True, related_name='donations')
    donation_type = models.CharField(max_length=20, choices=DONATION_TYPES)
    amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    in_kind_description = models.TextField(blank=True)
    in_kind_estimated_value = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    donation_date = models.DateField()
    purpose = models.CharField(max_length=200, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='received')
    payment_method = models.CharField(max_length=30, choices=PAYMENT_METHODS, blank=True)
    transaction_reference = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)
    recorded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.donation_ref:
            from datetime import date
            year = date.today().year
            last = Donation.objects.filter(donation_ref__startswith=f'DON-{year}').count()
            self.donation_ref = f'DON-{year}-{str(last+1).zfill(5)}'
        super().save(*args, **kwargs)

    @property
    def allocated_amount(self):
        return self.allocations.aggregate(total=models.Sum('amount'))['total'] or 0

    @property
    def remaining_amount(self):
        if self.donation_type == 'cash' and self.amount:
            return self.amount - self.allocated_amount
        return 0

    class Meta:
        ordering = ['-donation_date', '-created_at']
        indexes = [
            models.Index(fields=['donation_date']),
            models.Index(fields=['status']),
            models.Index(fields=['donation_type']),
        ]


class DonationReceipt(models.Model):
    donation = models.OneToOneField(Donation, on_delete=models.CASCADE, related_name='receipt')
    receipt_number = models.CharField(max_length=30, unique=True)
    pdf_file = models.FileField(upload_to='receipts/', blank=True, null=True)
    emailed_at = models.DateTimeField(null=True, blank=True)
    email_status = models.CharField(max_length=20, default='pending',
        choices=[('pending','Pending'),('sent','Sent'),('failed','Failed')])
    created_at = models.DateTimeField(auto_now_add=True)


class DonationAllocation(models.Model):
    ALLOCATION_TYPES = [
        ('education', 'Education'), ('food', 'Food'),
        ('medical', 'Medical'), ('clothing', 'Clothing'), ('general', 'General'),
    ]
    donation = models.ForeignKey(Donation, on_delete=models.CASCADE, related_name='allocations')
    beneficiary = models.ForeignKey(Beneficiary, on_delete=models.SET_NULL, null=True, blank=True)
    assistance_request = models.ForeignKey(AssistanceRequest, on_delete=models.SET_NULL, null=True, blank=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    allocation_type = models.CharField(max_length=50, choices=ALLOCATION_TYPES)
    description = models.TextField(blank=True)
    allocated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    allocated_at = models.DateTimeField(auto_now_add=True)
```

### communications/models.py
```python
from django.db import models
from django.contrib.auth.models import User

class Notification(models.Model):
    TYPES = [
        ('donation_received', 'Donation Received'),
        ('low_funds', 'Low Funds Alert'),
        ('request_approved', 'Request Approved'),
        ('request_rejected', 'Request Rejected'),
        ('update_available', 'Beneficiary Update'),
        ('system', 'System'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=50, choices=TYPES)
    title = models.CharField(max_length=255)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    link = models.URLField(max_length=500, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [models.Index(fields=['user', 'is_read'])]


class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    subject = models.CharField(max_length=255)
    body = models.TextField()
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']


class EmailLog(models.Model):
    EMAIL_TYPES = [
        ('donation_receipt', 'Donation Receipt'),
        ('low_funds_alert', 'Low Funds Alert'),
        ('broadcast', 'Broadcast'),
        ('update', 'Beneficiary Update'),
        ('password_reset', 'Password Reset'),
    ]
    recipient_email = models.EmailField()
    subject = models.CharField(max_length=255)
    email_type = models.CharField(max_length=50, choices=EMAIL_TYPES)
    status = models.CharField(max_length=20, default='pending',
        choices=[('pending','Pending'),('sent','Sent'),('failed','Failed')])
    celery_task_id = models.CharField(max_length=255, blank=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
```

---

## 5. RBAC Mixins (core/mixins.py)

```python
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied

class RoleRequiredMixin(LoginRequiredMixin):
    """Restrict views to specific roles."""
    allowed_roles = []

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        user_role = getattr(request.user, 'profile', None)
        if user_role and user_role.role in self.allowed_roles:
            return super().dispatch(request, *args, **kwargs)
        raise PermissionDenied

class AdminRequiredMixin(RoleRequiredMixin):
    allowed_roles = ['admin']

class StaffRequiredMixin(RoleRequiredMixin):
    allowed_roles = ['admin', 'staff']

class DonorRequiredMixin(RoleRequiredMixin):
    allowed_roles = ['donor']
```

---

## 6. Celery Tasks (donations/tasks.py)

```python
from celery import shared_task
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.conf import settings
import weasyprint
import os

@shared_task(bind=True, max_retries=3)
def send_donation_receipt(self, donation_id):
    from apps.donations.models import Donation, DonationReceipt
    from apps.communications.models import EmailLog
    from django.utils import timezone

    donation = Donation.objects.select_related('donor__user', 'receipt').get(id=donation_id)
    receipt = donation.receipt

    # Generate PDF
    html = render_to_string('donations/receipt_pdf.html', {'donation': donation})
    pdf = weasyprint.HTML(string=html, base_url=settings.BASE_DIR).write_pdf()

    # Save PDF
    pdf_filename = f'receipts/{receipt.receipt_number}.pdf'
    pdf_path = os.path.join(settings.MEDIA_ROOT, pdf_filename)
    os.makedirs(os.path.dirname(pdf_path), exist_ok=True)
    with open(pdf_path, 'wb') as f:
        f.write(pdf)
    receipt.pdf_file = pdf_filename
    receipt.save()

    # Send email
    if donation.donor and donation.donor.user.email:
        log = EmailLog.objects.create(
            recipient_email=donation.donor.user.email,
            subject=f'Donation Receipt - {receipt.receipt_number}',
            email_type='donation_receipt',
        )
        try:
            email = EmailMessage(
                subject=log.subject,
                body=render_to_string('emails/donation_receipt.html', {'donation': donation}),
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[log.recipient_email],
            )
            email.content_subtype = 'html'
            email.attach_filename = f'{receipt.receipt_number}.pdf'
            email.attach(f'{receipt.receipt_number}.pdf', pdf, 'application/pdf')
            email.send()
            log.status = 'sent'
            log.sent_at = timezone.now()
        except Exception as exc:
            log.status = 'failed'
            log.error_message = str(exc)
            log.save()
            raise self.retry(exc=exc, countdown=60)
        log.save()
        receipt.emailed_at = log.sent_at
        receipt.email_status = log.status
        receipt.save()


@shared_task
def check_low_funds():
    """Periodic task — run every hour via Celery Beat."""
    from apps.donations.models import Donation, DonationAllocation
    from apps.communications.models import Notification
    from django.contrib.auth.models import User
    from django.db.models import Sum

    total_cash = Donation.objects.filter(donation_type='cash').aggregate(
        t=Sum('amount'))['t'] or 0
    total_allocated = DonationAllocation.objects.aggregate(
        t=Sum('amount'))['t'] or 0
    available = total_cash - total_allocated

    if available < settings.LOW_FUNDS_THRESHOLD:
        admins = User.objects.filter(profile__role='admin')
        for admin in admins:
            Notification.objects.create(
                user=admin,
                notification_type='low_funds',
                title='⚠️ Low Funds Alert',
                message=f'Available funds are TZS {available:,.0f}, below the threshold of TZS {settings.LOW_FUNDS_THRESHOLD:,.0f}.',
                link='/admin/dashboard/'
            )
```

---

## 7. URL Configuration (config/urls.py)

```python
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('django-admin/', admin.site.urls),
    path('', include('apps.core.urls')),             # Landing page
    path('accounts/', include('apps.accounts.urls')),
    path('dashboard/', include('apps.core.dashboard_urls')),  # Role-based redirect
    path('admin/', include('apps.core.admin_urls')),
    path('staff/', include('apps.core.staff_urls')),
    path('donor/', include('apps.donors.urls')),
    path('beneficiaries/', include('apps.beneficiaries.urls')),
    path('donations/', include('apps.donations.urls')),
    path('communications/', include('apps.communications.urls')),
    path('reports/', include('apps.reports.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

---

## 8. Key Views (donations/views.py excerpt)

```python
from django.views.generic import CreateView, ListView, DetailView
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from apps.core.mixins import StaffRequiredMixin
from .models import Donation, DonationReceipt
from .tasks import send_donation_receipt
from apps.communications.models import Notification
from django.contrib.auth.models import User
import uuid

class DonationCreateView(StaffRequiredMixin, SuccessMessageMixin, CreateView):
    model = Donation
    fields = ['donor', 'donation_type', 'amount', 'in_kind_description',
              'in_kind_estimated_value', 'donation_date', 'purpose',
              'payment_method', 'transaction_reference', 'notes']
    template_name = 'donations/donation_form.html'
    success_url = reverse_lazy('donations:list')
    success_message = "Donation recorded successfully!"

    def form_valid(self, form):
        form.instance.recorded_by = self.request.user
        response = super().form_valid(form)
        donation = self.object

        # Create receipt
        year = donation.donation_date.year
        count = DonationReceipt.objects.count()
        receipt = DonationReceipt.objects.create(
            donation=donation,
            receipt_number=f'REC-{year}-{str(count+1).zfill(5)}'
        )

        # Queue async tasks
        send_donation_receipt.delay(donation.id)

        # Notify admins
        admins = User.objects.filter(profile__role='admin')
        for admin in admins:
            Notification.objects.create(
                user=admin,
                notification_type='donation_received',
                title='New Donation Received',
                message=f'A new donation ({donation.donation_ref}) has been recorded.',
                link=f'/donations/{donation.pk}/'
            )

        return response
```

---

## 9. Dashboard View (admin stats)

```python
from django.views.generic import TemplateView
from django.db.models import Sum, Count
from apps.core.mixins import AdminRequiredMixin
from apps.donations.models import Donation, DonationAllocation
from apps.beneficiaries.models import Beneficiary, AssistanceRequest
from apps.donors.models import Donor
from datetime import date
import json

class AdminDashboardView(AdminRequiredMixin, TemplateView):
    template_name = 'admin_panel/dashboard.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        today = date.today()

        # KPI Cards
        total_cash = Donation.objects.filter(donation_type='cash').aggregate(
            t=Sum('amount'))['t'] or 0
        total_allocated = DonationAllocation.objects.aggregate(
            t=Sum('amount'))['t'] or 0

        ctx.update({
            'total_donations': total_cash,
            'available_funds': total_cash - total_allocated,
            'total_donors': Donor.objects.count(),
            'active_beneficiaries': Beneficiary.objects.filter(status='active').count(),
            'pending_requests': AssistanceRequest.objects.filter(status='pending').count(),
            'recent_donations': Donation.objects.select_related('donor__user').order_by('-created_at')[:5],
            'pending_requests_list': AssistanceRequest.objects.filter(status='pending').select_related('beneficiary').order_by('-created_at')[:5],
            # Chart data (JSON for Chart.js)
            'monthly_chart_data': json.dumps(self._get_monthly_donations()),
            'donation_type_data': json.dumps(self._get_donation_type_split()),
        })
        return ctx

    def _get_monthly_donations(self):
        from django.db.models.functions import TruncMonth
        data = (Donation.objects.filter(donation_type='cash')
            .annotate(month=TruncMonth('donation_date'))
            .values('month')
            .annotate(total=Sum('amount'))
            .order_by('month'))
        return {
            'labels': [d['month'].strftime('%b %Y') for d in data],
            'values': [float(d['total']) for d in data],
        }

    def _get_donation_type_split(self):
        cash = Donation.objects.filter(donation_type='cash').aggregate(t=Sum('amount'))['t'] or 0
        inkind = Donation.objects.filter(donation_type='in_kind').aggregate(t=Sum('in_kind_estimated_value'))['t'] or 0
        return {'cash': float(cash), 'inkind': float(inkind)}
```

---

## 10. Docker Setup

### docker-compose.yml
```yaml
version: '3.9'

services:
  db:
    image: postgres:16
    environment:
      POSTGRES_DB: ${DB_NAME}
      POSTGRES_USER: ${DB_USER}
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data/

  redis:
    image: redis:7-alpine

  web:
    build: .
    command: gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 3
    volumes:
      - .:/app
      - media_data:/app/media
    ports:
      - "8000:8000"
    env_file: .env
    depends_on:
      - db
      - redis

  celery:
    build: .
    command: celery -A config worker --loglevel=info
    env_file: .env
    depends_on:
      - db
      - redis

  celery-beat:
    build: .
    command: celery -A config beat --loglevel=info --scheduler django_celery_beat.schedulers:DatabaseScheduler
    env_file: .env
    depends_on:
      - db
      - redis

volumes:
  postgres_data:
  media_data:
```

---

## 11. Development Commands

```bash
# Run migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Run development server
python manage.py runserver

# Run Celery worker (separate terminal)
celery -A config worker --loglevel=info

# Run Celery beat scheduler
celery -A config beat --loglevel=info

# Collect static files
python manage.py collectstatic

# Run tests
python manage.py test apps/

# Load initial data (fixtures)
python manage.py loaddata initial_data.json
```
