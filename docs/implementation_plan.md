# CharityOS — Django Full-Stack SaaS Implementation Plan

A **Charity Management System** for orphan support organizations in Tanzania. Built with Django 5.x, PostgreSQL, Celery + Redis, and a dark SaaS dashboard UI matching the HTML sample.

---

## User Review Required

> [!IMPORTANT]
> **Database**: The plan uses SQLite for initial development (`db.sqlite3`) so you can run immediately without PostgreSQL. The code is PostgreSQL-ready — just update `.env` when deploying.

> [!IMPORTANT]
> **Celery/Redis**: For development, email tasks will be logged to console. Celery is configured but optional for local dev. The system gracefully falls back to synchronous execution.

> [!WARNING]
> **Tailwind CSS**: Per the docs, the frontend uses Tailwind + Alpine.js + HTMX. However, the HTML sample uses **custom vanilla CSS** with a dark SaaS aesthetic. I will follow the HTML sample's design system (dark mode, DM Sans font, accent colors) and use **vanilla CSS with component-based files** to keep the codebase modular and readable. No Tailwind build step needed.

---

## Proposed Changes

### Phase 1: Project Foundation

#### [NEW] Project scaffold & configuration

| File | Purpose |
|------|---------|
| `charity_cms/manage.py` | Django management entry point |
| `charity_cms/config/__init__.py` | Celery app auto-discovery |
| `charity_cms/config/settings/base.py` | Core settings (DB, auth, static, media, celery) |
| `charity_cms/config/settings/development.py` | Debug=True, SQLite, console email |
| `charity_cms/config/settings/production.py` | PostgreSQL, SMTP, whitenoise |
| `charity_cms/config/urls.py` | Root URL router |
| `charity_cms/config/celery.py` | Celery application setup |
| `charity_cms/config/wsgi.py` | WSGI entry point |
| `charity_cms/.env` | Environment variables template |
| `charity_cms/requirements.txt` | Python dependencies |

---

### Phase 2: Django Apps (7 apps under `apps/`)

#### [NEW] `apps/accounts/` — Authentication & User Profiles
- `models.py` — `UserProfile` (OneToOne to User, role field: admin/staff/donor)
- `forms.py` — `DonorRegistrationForm`, `LoginForm`, `ProfileUpdateForm`
- `views.py` — Login, logout, register, profile, password reset redirect
- `urls.py` — `/accounts/login/`, `/accounts/register/`, `/accounts/profile/`
- `signals.py` — Auto-create UserProfile on User creation
- `admin.py` — Register UserProfile in Django admin

#### [NEW] `apps/donors/` — Donor Management
- `models.py` — `Donor` model (linked to User, organization, address, etc.)
- `forms.py` — `DonorForm`
- `views.py` — Donor dashboard, donation history, sponsored beneficiaries
- `urls.py` — `/donor/dashboard/`, `/donor/history/`
- `admin.py` — Register Donor

#### [NEW] `apps/beneficiaries/` — Beneficiary & Assistance Requests
- `models.py` — `Beneficiary`, `DonorBeneficiaryLink`, `AssistanceRequest`, `BeneficiaryUpdate`
- `forms.py` — `BeneficiaryForm`, `AssistanceRequestForm`, `BeneficiaryUpdateForm`
- `views.py` — CRUD views, search/filter, request approval/rejection
- `urls.py` — `/beneficiaries/`, `/beneficiaries/create/`, `/beneficiaries/<id>/`
- `admin.py` — Register all models

#### [NEW] `apps/donations/` — Donation, Receipt & Allocation
- `models.py` — `Donation`, `DonationReceipt`, `DonationAllocation`
- `forms.py` — `DonationForm`, `AllocationForm`
- `views.py` — Record donation, list, detail, allocate funds
- `urls.py` — `/donations/`, `/donations/create/`, `/donations/<id>/allocate/`
- `tasks.py` — Celery task for receipt PDF + email
- `admin.py` — Register all models

#### [NEW] `apps/communications/` — Notifications, Messages, Email Logs
- `models.py` — `Notification`, `Message`, `EmailLog`
- `forms.py` — `MessageForm`, `BroadcastForm`
- `views.py` — Inbox, compose, notifications list, mark as read
- `urls.py` — `/communications/inbox/`, `/communications/notifications/`
- `admin.py` — Register all models

#### [NEW] `apps/reports/` — PDF Reports & Data Export
- `views.py` — Generate monthly/annual summary PDFs, donor reports
- `urls.py` — `/reports/monthly/`, `/reports/annual/`, `/reports/donors/`
- `utils.py` — WeasyPrint PDF generation helpers

#### [NEW] `apps/core/` — Shared Utilities & Audit Trail
- `models.py` — `AuditLog`
- `mixins.py` — `RoleRequiredMixin`, `AdminRequiredMixin`, `StaffRequiredMixin`, `DonorRequiredMixin`
- `context_processors.py` — Global context (notifications count, user role, org name)
- `decorators.py` — `@role_required` function decorator
- `utils.py` — Audit logging helper, reference number generators
- `templatetags/charity_tags.py` — Custom template tags (currency formatting, initials)
- `urls.py` — Landing page, dashboard redirect
- `views.py` — Landing page, role-based dashboard redirect

---

### Phase 3: Template System (Component-Based Architecture)

The UI follows the HTML sample's dark SaaS design. Templates are organized into **pages** and **reusable components**:

```
templates/
├── base.html                          # Master layout (sidebar + topbar shell)
├── components/
│   ├── sidebar.html                   # Navigation sidebar
│   ├── topbar.html                    # Top bar with actions
│   ├── kpi_card.html                  # Reusable KPI stat card
│   ├── data_table.html                # Reusable data table component
│   ├── modal.html                     # Modal dialog component
│   ├── alert.html                     # Flash message/alert component
│   ├── pagination.html                # Pagination component
│   ├── empty_state.html               # Empty state placeholder
│   ├── avatar.html                    # User avatar component
│   ├── badge.html                     # Status badge component
│   └── form_field.html                # Styled form field component
├── landing/
│   └── index.html                     # Public landing page
├── accounts/
│   ├── login.html                     # Login page
│   ├── register.html                  # Donor registration page
│   └── profile.html                   # User profile page
├── admin_panel/
│   └── dashboard.html                 # Admin dashboard (matches HTML sample)
├── staff_panel/
│   └── dashboard.html                 # Staff dashboard
├── donor_portal/
│   └── dashboard.html                 # Donor dashboard
├── beneficiaries/
│   ├── list.html                      # Beneficiary list with filters
│   ├── detail.html                    # Beneficiary profile detail
│   ├── form.html                      # Create/edit beneficiary form
│   └── requests.html                  # Assistance requests list
├── donations/
│   ├── list.html                      # Donations list
│   ├── detail.html                    # Donation detail + allocation
│   ├── form.html                      # Record donation form
│   └── receipt_pdf.html               # PDF receipt template
├── communications/
│   ├── inbox.html                     # Messages inbox
│   ├── compose.html                   # Compose message
│   └── notifications.html            # Notifications list
└── reports/
    └── report_list.html               # Reports index page
```

---

### Phase 4: Static Assets (Component CSS)

```
static/
├── css/
│   ├── base.css                       # Design tokens, reset, typography
│   ├── components/
│   │   ├── sidebar.css                # Sidebar styles
│   │   ├── topbar.css                 # Topbar styles
│   │   ├── kpi.css                    # KPI card styles
│   │   ├── table.css                  # Data table styles
│   │   ├── forms.css                  # Form styles
│   │   ├── buttons.css                # Button styles
│   │   ├── badges.css                 # Badge/pill styles
│   │   ├── modals.css                 # Modal styles
│   │   └── charts.css                 # Chart container styles
│   ├── pages/
│   │   ├── landing.css                # Landing page styles
│   │   ├── dashboard.css              # Dashboard layout
│   │   └── auth.css                   # Login/register pages
│   └── main.css                       # Imports all component CSS files
├── js/
│   ├── main.js                        # Global interactions
│   ├── charts.js                      # Chart.js initialization
│   ├── sidebar.js                     # Mobile sidebar toggle
│   └── notifications.js              # Notification mark-as-read
└── images/
    └── org_logo.png                   # Organization logo placeholder
```

---

### Phase 5: Context Folder & Documentation

#### [NEW] `context/agents.md`
Comprehensive documentation covering:
- Project overview and architecture
- Django app structure and responsibilities
- Database models and relationships
- URL routing map
- Template hierarchy
- RBAC system explanation
- Celery tasks
- Development workflow

---

### Phase 6: Docker & DevOps

| File | Purpose |
|------|---------|
| `charity_cms/Dockerfile` | Multi-stage Docker build |
| `charity_cms/docker-compose.yml` | PostgreSQL + Redis + Web + Celery |
| `charity_cms/.dockerignore` | Exclude unnecessary files |

---

## Verification Plan

### Automated Tests
```bash
cd charity_cms
python manage.py check                    # System check
python manage.py makemigrations --check   # Verify migrations
python manage.py migrate                  # Apply migrations
python manage.py runserver 0.0.0.0:8000   # Start dev server
```

### Manual Verification
- Visit landing page at `http://localhost:8000/`
- Login flow at `/accounts/login/`
- Admin dashboard at `/admin/dashboard/`
- Verify sidebar navigation links
- Check KPI cards render correctly
- Verify RBAC redirects work per role

---

## Open Questions

> [!NOTE]
> **Organization Name**: The HTML sample uses "CharityOS" as branding. Should I keep this or use a specific organization name?

> [!NOTE]
> **Initial Data**: Should I create a management command or fixture to seed demo data (sample donors, beneficiaries, donations) for testing?
