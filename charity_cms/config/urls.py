"""
CharityOS — Root URL Configuration
====================================
Maps top-level URL prefixes to individual app URL modules.
Each app has its own urls.py for clean separation of concerns.

URL Structure:
    /                       → Landing page (public)
    /accounts/              → Auth (login, register, profile, password reset)
    /dashboard/             → Role-based dashboard redirect
    /admin-panel/           → Admin dashboard & management views
    /staff/                 → Staff-specific views
    /donor/                 → Donor portal
    /beneficiaries/         → Beneficiary management
    /donations/             → Donation recording & tracking
    /communications/        → Messages & notifications
    /reports/               → PDF reports & data export
    /django-admin/          → Django's built-in admin (for superusers)
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # --- Django Built-in Admin (superuser access only) ---
    path('django-admin/', admin.site.urls),

    # --- Public & Core Routes ---
    path('', include('apps.core.urls')),

    # --- Authentication ---
    path('accounts/', include('apps.accounts.urls')),

    # --- Role-Based Dashboards ---
    path('admin-panel/', include(('apps.core.admin_urls', 'admin_panel'))),
    path('staff/', include(('apps.core.staff_urls', 'staff_panel'))),
    path('donor/', include('apps.donors.urls')),

    # --- Feature Modules ---
    path('beneficiaries/', include('apps.beneficiaries.urls')),
    path('donations/', include('apps.donations.urls')),
    path('communications/', include('apps.communications.urls')),
    path('reports/', include('apps.reports.urls')),
]

# Serve media files in development (uploaded photos, PDFs, etc.)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
