# CharityOS 🌍

> A comprehensive, production-ready SaaS platform for non-profit organizations managing orphan support programs in Tanzania. Built with Django, Celery, and a modern dark-themed UI.

---

## 📋 Table of Contents
1. [What is CharityOS?](#-what-is-charityos)
2. [Who is it For?](#-who-is-it-for)
3. [Tech Stack](#-tech-stack)

4. [Project Folder Structure](#-project-folder-structure)
5. [Documentation Reference Guide](#-documentation-reference-guide)
6. [Data Models Overview](#-data-models-overview)
7. [Role-Based Access Control (RBAC)](#-role-based-access-control-rbac)
8. [URL Routing Map](#-url-routing-map)
9. [CSS Design System](#-css-design-system)
10. [Getting Started (Development)](#-getting-started-development)
11. [Docker Deployment](#-docker-deployment)
12. [Background Tasks (Celery)](#-background-tasks-celery)
13. [Security & Auditing](#-security--auditing)
14. [Environment Variables](#-environment-variables)

---

## 🌟 What is CharityOS?
CharityOS is a full-stack web application designed to help NGOs and charities manage orphan sponsorship programs. It replaces fragmented spreadsheets, paper records, and disconnected email threads with a single, centralized platform that:

- **Tracks every orphan** from enrollment to graduation — their demographics, education, health, guardian details, and assistance needs.
- **Logs every donation** — whether cash (via M-Pesa, bank transfer, etc.) or in-kind (food, clothing, supplies) — and tracks where every shilling goes through a strict fund allocation system.
- **Connects donors to children** — donors get a personal portal showing exactly which children they sponsor, the latest progress updates, and downloadable tax receipts.
- **Automates operations** — PDF receipts are generated and emailed automatically, low-fund alerts fire on schedule, and system-wide audit logs track every change made by every user.

---

## 👥 Who is it For?

| Role | What They Do | Dashboard |
|------|-------------|-----------|
| **Admin** | Full system access. Manage users, approve assistance requests, view financial reports, configure system settings. | Admin Panel (`/admin-panel/`) |
| **Staff** | On-the-ground team. Register beneficiaries, record donations, submit assistance requests, log progress updates. | Staff Panel (`/staff/`) |
| **Donor** | External supporter. View sponsored children, download receipts, see impact updates. | Donor Portal (`/donor/`) |

---

## 🏗️ Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Backend** | Django 4.2 (Python 3.10+) | Web framework, ORM, auth, templating |
| **Database** | PostgreSQL (prod) / SQLite (dev) | Relational data storage |
| **Task Queue** | Celery 5.4 + Redis | Async PDF generation, email sending, scheduled jobs |
| **Scheduler** | django-celery-beat | Cron-style periodic tasks (e.g., nightly low-fund check) |
| **PDF Engine** | WeasyPrint 62.3 | HTML → PDF conversion for receipts and reports |
| **Frontend** | Django Templates + HTMX | Server-side rendering with dynamic partial reloads |
| **Styling** | Vanilla CSS (custom design system) | Dark-themed SaaS UI, no Tailwind/Bootstrap |
| **Icons** | Phosphor Icons (CDN) | Lightweight icon library |
| **Charts** | Chart.js (CDN) | Dashboard KPI visualizations |
| **Forms** | django-crispy-forms | Consistent form rendering |
| **Static Files** | WhiteNoise | Production static file serving |
| **Images** | Pillow 10.4 | Avatar and photo processing |
| **Deployment** | Docker + Gunicorn | Containerized production deployment |

### Why Vanilla CSS instead of Tailwind?
- **Zero build step** — no npm, no Webpack, no PostCSS pipeline.
- **Easy to read** — any developer familiar with CSS can understand the styles immediately.
- **Lightweight** — the entire CSS system is ~10KB across 10 files.
- **Maintainable** — component-based architecture mirrors the template structure.

---

## 📁 Project Folder Structure

```
sarah/                                  ← Repository Root
├── README.md                           ← THIS FILE — Master project guide
├── Dockerfile                          ← Docker image definition
├── docker-compose.yml                  ← Multi-container orchestration (Postgres, Redis, Web, Celery)
├── entrypoint.sh                       ← Container startup script (migrate + collectstatic)
├── .gitignore                          ← Git exclusions (venv, .env, __pycache__, media)
├── .dockerignore                       ← Docker build exclusions
│
├── context/                            ← AI Agent context files
│   └── agents.md                       ← Architecture summary for AI coding assistants
│
├── docs/                               ← 📚 DETAILED DESIGN DOCUMENTATION
│   ├── 01_SRS.md                       ← Software Requirements Specification
│   ├── 02_DB_SCHEMA.md                 ← Original database schema design
│   ├── 03_DATA_FLOW.md                 ← Data flow diagrams and process maps
│   ├── 04_DJANGO_BUILD_GUIDE.md        ← Step-by-step build instructions
│   ├── implementation_plan.md          ← Implementation plan and phases
│   ├── charity_cms_saas_dashboard.html ← 🎨 Original HTML/CSS prototype (DESIGN REFERENCE)
│   └── architecture/                   ← In-depth technical architecture
│       ├── overview.md                 ← Request lifecycle, Celery flow, RBAC explanation
│       └── data_models.md              ← Complete ERD, all model relationships
│
└── charity_cms/                        ← 🏠 DJANGO PROJECT ROOT
    ├── manage.py                       ← Django management CLI
    ├── requirements.txt                ← Python dependencies (pinned versions)
    ├── .env                            ← Environment variables (SECRET_KEY, DB, etc.) ⚠️ NOT IN GIT
    ├── db.sqlite3                      ← SQLite dev database ⚠️ NOT IN GIT
    │
    ├── config/                         ← ⚙️ Django project configuration
    │   ├── __init__.py                 ← Makes config a Python package
    │   ├── urls.py                     ← Root URL router (maps prefixes to apps)
    │   ├── wsgi.py                     ← WSGI entry point (Gunicorn)
    │   ├── asgi.py                     ← ASGI entry point (future async)
    │   ├── celery.py                   ← Celery application setup and autodiscovery
    │   └── settings/                   ← Split settings for environment isolation
    │       ├── __init__.py             ← Imports from DJANGO_SETTINGS_MODULE
    │       ├── base.py                 ← Shared settings (INSTALLED_APPS, middleware, templates)
    │       ├── development.py          ← Dev overrides (DEBUG=True, SQLite, console email)
    │       └── production.py           ← Prod overrides (Postgres, S3 storage, HTTPS)
    │
    ├── apps/                           ← 📦 DJANGO APPLICATIONS (business logic)
    │   ├── __init__.py
    │   ├── core/                       ← System-wide: audit logs, RBAC mixins, templatetags, dashboards
    │   │   └── README.md               ← Detailed docs for this app
    │   ├── accounts/                   ← Authentication: UserProfile, login, registration, signals
    │   │   └── README.md
    │   ├── beneficiaries/              ← Orphan management: profiles, needs, progress, sponsors
    │   │   └── README.md
    │   ├── donations/                  ← Financial tracking: cash/in-kind, allocations, receipts, Celery tasks
    │   │   └── README.md
    │   ├── donors/                     ← Donor portal: dashboard, donation history, linked children
    │   │   └── README.md
    │   ├── communications/             ← Internal messaging: inbox, notifications, email logs
    │   │   └── README.md
    │   └── reports/                    ← PDF generators: monthly summary, donor directory
    │       └── README.md
    │
    ├── templates/                      ← 🖼️ HTML TEMPLATES (Django template engine)
    │   ├── base.html                   ← Master layout (sidebar + topbar + content area)
    │   ├── components/                 ← Reusable UI fragments (sidebar, topbar, KPI cards)
    │   ├── landing/                    ← Public landing page (index.html)
    │   ├── accounts/                   ← Login, register, profile templates
    │   ├── admin_panel/                ← Admin dashboard (KPIs, charts, recent activity)
    │   ├── staff_panel/                ← Staff dashboard (quick actions, pending requests)
    │   ├── donor_portal/               ← Donor dashboard (impact metrics, children feed)
    │   ├── beneficiaries/              ← List, detail, form templates
    │   ├── donations/                  ← List, form, detail templates
    │   ├── communications/             ← Inbox, compose, message detail
    │   └── reports/                    ← Report selection page
    │
    └── static/                         ← 🎨 STATIC ASSETS
        ├── css/
        │   ├── main.css                ← Entry point (imports all other CSS files)
        │   ├── base.css                ← CSS custom properties (design tokens, resets)
        │   ├── components/             ← Modular CSS components
        │   │   ├── sidebar.css         ← Left navigation sidebar
        │   │   ├── topbar.css          ← Top header bar
        │   │   ├── kpi.css             ← KPI metric cards
        │   │   ├── panels.css          ← Content panels, cards, request items
        │   │   ├── table.css           ← Data tables
        │   │   ├── badges.css          ← Status badges (active, pending, etc.)
        │   │   ├── buttons.css         ← Buttons (primary, secondary, action, sm)
        │   │   └── forms.css           ← Form inputs, labels, groups, rows
        │   └── pages/                  ← Page-specific overrides (if needed)
        ├── js/                         ← JavaScript (Chart.js configs, sidebar toggle)
        └── images/                     ← Static images (logos, placeholders)
```

---

## 📚 Documentation Reference Guide

CharityOS maintains its design documentation in the `docs/` folder. **Always reference these files** before making architectural changes:

| Document | Purpose | When to Read |
|----------|---------|-------------|
| [`docs/01_SRS.md`](docs/01_SRS.md) | Software Requirements Specification — functional and non-functional requirements | Understanding what the system should do |
| [`docs/02_DB_SCHEMA.md`](docs/02_DB_SCHEMA.md) | Original database schema design with all table definitions | Before adding/modifying models |
| [`docs/03_DATA_FLOW.md`](docs/03_DATA_FLOW.md) | Data flow diagrams — how data moves through the system | Understanding business logic flows |
| [`docs/04_DJANGO_BUILD_GUIDE.md`](docs/04_DJANGO_BUILD_GUIDE.md) | Step-by-step Django implementation guide | Building new features |
| [`docs/charity_cms_saas_dashboard.html`](docs/charity_cms_saas_dashboard.html) | **THE DESIGN REFERENCE** — open in a browser to see the target UI | Before touching templates or CSS |
| [`docs/architecture/overview.md`](docs/architecture/overview.md) | Request lifecycle, Celery flow, RBAC enforcement | Understanding how views work |
| [`docs/architecture/data_models.md`](docs/architecture/data_models.md) | Complete ERD and model relationships | Before writing queries |

> **Tip:** Open `docs/charity_cms_saas_dashboard.html` in your browser. This is the exact dark-themed SaaS design that all Django templates replicate.

---

## 🗄️ Data Models Overview

CharityOS has **10 database models** across 6 apps. Here is every model, every field, and how they connect:

### `accounts.UserProfile` — Extends Django User
| Field | Type | Description |
|-------|------|-------------|
| `user` | OneToOne → `auth.User` | The Django auth user this extends |
| `role` | CharField (choices) | `admin`, `staff`, or `donor` — determines dashboard access |
| `phone` | CharField | Contact phone (e.g., +255712345678) |
| `avatar` | ImageField | Profile picture (uploads to `avatars/`) |
| `created_at` | DateTimeField | Auto-set on creation |
| `updated_at` | DateTimeField | Auto-set on every save |

### `donors.Donor` — Donor Business Profile
| Field | Type | Description |
|-------|------|-------------|
| `user` | OneToOne → `auth.User` | Links to the user account |
| `organization` | CharField | Company/NGO name (for corporate donors) |
| `address` | TextField | Mailing address |
| `national_id` | CharField | Government ID for tax receipts |
| `is_anonymous` | BooleanField | Hide name in public listings |
| `notes` | TextField | Internal admin notes |
| **Computed** | `total_donated` | Sum of all cash donations (property) |
| **Computed** | `donation_count` | Count of all donations (property) |
| **Computed** | `display_name` | Respects anonymity preference (property) |

### `beneficiaries.Beneficiary` — Orphan Profile
| Field | Type | Description |
|-------|------|-------------|
| `beneficiary_code` | CharField (auto) | Unique ID like `BEN-2025-0001` |
| `first_name`, `last_name` | CharField | Child's name |
| `date_of_birth` | DateField | Used to calculate `age` property |
| `gender` | CharField (choices) | `male` or `female` |
| `photo` | ImageField | Child's photo |
| `school_name`, `school_grade` | CharField | Education details |
| `health_status` | TextField | Medical notes |
| `guardian_name`, `guardian_phone`, `guardian_relationship` | CharField | Guardian info |
| `location_region`, `location_district` | CharField | Geographic location |
| `date_enrolled` | DateField | Program enrollment date |
| `status` | CharField (choices) | `active`, `inactive`, or `graduated` |
| `registered_by` | FK → `auth.User` | Staff who registered the child |

### `beneficiaries.AssistanceRequest` — Needs Tracking
| Field | Type | Description |
|-------|------|-------------|
| `request_ref` | CharField (auto) | Unique ID like `REQ-2025-0001` |
| `beneficiary` | FK → `Beneficiary` | The child this need is for |
| `requested_by` | FK → `auth.User` | Staff who submitted the request |
| `request_type` | CharField (choices) | `education`, `food`, `medical`, `clothing`, `other` |
| `description` | TextField | Detailed description of the need |
| `estimated_cost` | DecimalField | Estimated cost in TZS |
| `status` | CharField (choices) | `pending` → `approved` → `fulfilled` (or `rejected`) |
| `reviewed_by` | FK → `auth.User` | Admin who approved/rejected |

### `beneficiaries.DonorBeneficiaryLink` — Sponsorship Mapping
| Field | Type | Description |
|-------|------|-------------|
| `donor` | FK → `Donor` | The sponsoring donor |
| `beneficiary` | FK → `Beneficiary` | The sponsored child |
| `start_date` | DateField | When sponsorship began |
| `end_date` | DateField (nullable) | NULL = active sponsorship |
| `is_active` | BooleanField | Quick filter for active links |

### `beneficiaries.BeneficiaryUpdate` — Progress Journal
| Field | Type | Description |
|-------|------|-------------|
| `beneficiary` | FK → `Beneficiary` | The child this update is about |
| `title` | CharField | Update headline |
| `content` | TextField | Narrative for donors |
| `photo` | ImageField | Optional progress photo |
| `created_by` | FK → `auth.User` | Staff who wrote the update |
| `notified_donors` | BooleanField | Whether linked donors were alerted |

### `donations.Donation` — Financial Ledger
| Field | Type | Description |
|-------|------|-------------|
| `donation_ref` | CharField (auto) | Unique ID like `DON-2025-00001` |
| `donor` | FK → `Donor` (nullable) | NULL = anonymous donation |
| `donation_type` | CharField (choices) | `cash` or `in_kind` |
| `amount` | DecimalField | Cash amount in TZS |
| `payment_method` | CharField (choices) | `cash`, `mpesa`, `tigopesa`, `bank`, `other` |
| `transaction_reference` | CharField | Mobile money / bank reference |
| `in_kind_description` | TextField | Description of physical items |
| `in_kind_estimated_value` | DecimalField | Estimated value of in-kind items |
| `donation_date` | DateField | When the donation was received |
| `purpose` | CharField | Fund designation (e.g., "Education Fund") |
| `status` | CharField (choices) | `received` → `partial` → `allocated` |
| `recorded_by` | FK → `auth.User` | Staff who logged the donation |
| **Computed** | `allocated_amount` | Sum of all allocations (property) |
| **Computed** | `remaining_amount` | `amount - allocated_amount` (property) |

### `donations.DonationReceipt` — PDF Receipt Record
| Field | Type | Description |
|-------|------|-------------|
| `donation` | OneToOne → `Donation` | The donation this receipt is for |
| `receipt_number` | CharField | Unique receipt number |
| `pdf_file` | FileField | Generated PDF (uploads to `receipts/`) |
| `emailed_at` | DateTimeField | When the receipt was emailed |
| `email_status` | CharField (choices) | `pending`, `sent`, or `failed` |

### `donations.DonationAllocation` — Fund Distribution
| Field | Type | Description |
|-------|------|-------------|
| `donation` | FK → `Donation` | Source donation |
| `beneficiary` | FK → `Beneficiary` | Recipient child |
| `assistance_request` | FK → `AssistanceRequest` | The specific need being funded |
| `amount` | DecimalField | Amount allocated in TZS |
| `allocation_type` | CharField (choices) | `education`, `food`, `medical`, `clothing`, `general` |
| `allocated_by` | FK → `auth.User` | Staff/admin who made the allocation |
| **Side Effect** | On `save()` | Updates parent `Donation.status` automatically |

### `communications.Notification` — System Alerts
| Field | Type | Description |
|-------|------|-------------|
| `user` | FK → `auth.User` | Recipient of the notification |
| `notification_type` | CharField (choices) | `donation_received`, `low_funds`, `request_approved`, etc. |
| `title` | CharField | Alert headline |
| `message` | TextField | Alert body |
| `is_read` | BooleanField | Read/unread status |
| `link` | URLField | Deep link to the relevant item |

### `communications.Message` — Internal Messaging
| Field | Type | Description |
|-------|------|-------------|
| `sender` | FK → `auth.User` | Who sent the message |
| `recipient` | FK → `auth.User` | Who receives the message |
| `subject` | CharField | Message subject line |
| `body` | TextField | Message content |
| `is_read` | BooleanField | Read/unread status |
| `read_at` | DateTimeField | When the message was read |

### `communications.EmailLog` — Outbound Email Audit
| Field | Type | Description |
|-------|------|-------------|
| `recipient_email` | EmailField | Destination email address |
| `subject` | CharField | Email subject line |
| `email_type` | CharField (choices) | `donation_receipt`, `low_funds_alert`, `broadcast`, etc. |
| `status` | CharField (choices) | `pending`, `sent`, or `failed` |
| `celery_task_id` | CharField | Celery task ID for tracking |
| `error_message` | TextField | Error details if sending failed |

### `core.AuditLog` — System-Wide Audit Trail
| Field | Type | Description |
|-------|------|-------------|
| `user` | FK → `auth.User` | Who performed the action |
| `content_type` | FK → `ContentType` | Which model was affected |
| `object_id` | PositiveIntegerField | PK of the affected record |
| `content_object` | GenericForeignKey | The actual affected object |
| `action` | CharField | `CREATE`, `UPDATE`, `DELETE`, `LOGIN`, etc. |
| `changes` | JSONField | What specifically changed |
| `ip_address` | GenericIPAddressField | IP of the user |

---

## 🔐 Role-Based Access Control (RBAC)

Every view is protected by custom mixins defined in `apps/core/mixins.py`:

```python
# Example: Only staff and admins can create donations
class DonationCreateView(StaffRequiredMixin, CreateView):
    ...

# Example: Only admins can view reports
class MonthlySummaryPDFView(AdminRequiredMixin, View):
    ...

# Example: Only donors can access the donor portal
class DonorDashboardView(DonorRequiredMixin, TemplateView):
    ...
```

| Mixin | Allowed Roles | Redirects To |
|-------|--------------|-------------|
| `AdminRequiredMixin` | `admin` only | Login page |
| `StaffRequiredMixin` | `admin` + `staff` | Login page |
| `DonorRequiredMixin` | `donor` only | Login page |

---

## 🗺️ URL Routing Map

| URL Prefix | App | Description |
|------------|-----|-------------|
| `/` | `core` | Landing page (public) |
| `/accounts/login/` | `accounts` | User login |
| `/accounts/register/` | `accounts` | Donor self-registration |
| `/dashboard/` | `core` | Role-based redirect to appropriate dashboard |
| `/admin-panel/` | `core` (admin_urls) | Admin dashboard with KPIs and charts |
| `/staff/` | `core` (staff_urls) | Staff dashboard with quick actions |
| `/donor/` | `donors` | Donor portal with impact metrics |
| `/beneficiaries/` | `beneficiaries` | CRUD for orphan records |
| `/donations/` | `donations` | Donation recording and tracking |
| `/communications/` | `communications` | Internal messaging inbox |
| `/reports/` | `reports` | PDF report generation |
| `/django-admin/` | Django built-in | Superuser-only Django admin |

---

## 🎨 CSS Design System

The UI uses a custom dark-themed design system built with CSS Custom Properties (variables):

### Design Tokens (`static/css/base.css`)
```css
:root {
    --bg: #0e0f11;              /* Page background */
    --surface: #16181d;          /* Card/panel background */
    --border: #23262f;           /* Border color */
    --text: #d4d4d8;             /* Primary text */
    --muted: #6b7280;            /* Secondary text */
    --accent: #6ee7b7;           /* Primary accent (green) */
    --accent2: #818cf8;          /* Secondary accent (indigo) */
    --warn: #fbbf24;             /* Warning (amber) */
    --error: #f87171;            /* Error (red) */
    --font-sans: 'DM Sans', sans-serif;
    --font-mono: 'DM Mono', monospace;
}
```

### Component Files (`static/css/components/`)
| File | Styles |
|------|--------|
| `sidebar.css` | Left navigation: logo, nav items, active states |
| `topbar.css` | Top header bar with page title and user info |
| `kpi.css` | KPI metric cards with labels and delta indicators |
| `panels.css` | Content cards, panel titles, request item lists |
| `table.css` | Data tables with striped rows and hover effects |
| `badges.css` | Status badges: `.badge-success`, `.badge-warn`, `.badge-error` |
| `buttons.css` | `.btn-primary`, `.btn-secondary`, `.btn-sm`, `.btn-action` |
| `forms.css` | `.form-input`, `.form-label`, `.form-group`, `.form-row` |

---

## 🚀 Getting Started (Development)

### Prerequisites
- Python 3.10+
- Redis server (for Celery background tasks)

### Quick Setup
```bash
# 1. Clone the repository
git clone https://github.com/troubleman96/Charity-Management-System.git
cd Charity-Management-System/charity_cms

# 2. Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# 3. Install Python dependencies
pip install -r requirements.txt

# 4. Set up environment variables (copy from template)
cp .env.example .env  # Then edit with your values

# 5. Run database migrations
python manage.py makemigrations
python manage.py migrate

# 6. Create your admin superuser
python manage.py createsuperuser

# 7. Start the development server
python manage.py runserver
# → Open http://localhost:8000/

# 8. (Optional) Start Celery worker in a separate terminal
source venv/bin/activate
celery -A config worker -l info
```

---

## 🐳 Docker Deployment

```bash
# Build and start all services (Postgres, Redis, Web, Celery)
docker-compose up --build -d

# Apply migrations
docker-compose exec web python manage.py migrate

# Create admin superuser
docker-compose exec web python manage.py createsuperuser

# Collect static files
docker-compose exec web python manage.py collectstatic --noinput
```

**Services:**
| Container | Image | Port | Purpose |
|-----------|-------|------|---------|
| `db` | postgres:14 | 5432 | PostgreSQL database |
| `redis` | redis:6-alpine | 6379 | Celery message broker |
| `web` | Custom (Gunicorn) | 8000 | Django web application |
| `celery` | Custom | — | Background task worker |

---

## ⏰ Background Tasks (Celery)

| Task | Location | Trigger | What it Does |
|------|----------|---------|-------------|
| `send_donation_receipt` | `apps/donations/tasks.py` | Called after every new donation | Renders HTML receipt → WeasyPrint PDF → emails to donor |
| `check_low_funds` | `apps/donations/tasks.py` | Periodic (nightly via celery-beat) | Checks total unallocated cash balance; creates admin notification if below threshold |

---

## 🛡️ Security & Auditing

1. **Immutable Audit Trail**: Every significant action calls `log_action()` from `apps.core.utils`, which creates an `AuditLog` record containing the user, action type, affected model, changes made, and IP address.
2. **RBAC Enforcement**: No view is ever publicly accessible except the landing page and login/register. Every other view requires authentication AND the correct role via mixins.
3. **CSRF Protection**: Django's built-in CSRF middleware is active on all POST forms.
4. **Password Security**: Django's password validators enforce minimum length and complexity.

---

## 🔧 Environment Variables

The `.env` file in `charity_cms/` must contain:

| Variable | Example | Description |
|----------|---------|-------------|
| `SECRET_KEY` | `django-insecure-abc123...` | Django secret key (change in production!) |
| `DEBUG` | `True` | Set to `False` in production |
| `DJANGO_SETTINGS_MODULE` | `config.settings.development` | Which settings file to use |
| `DATABASE_URL` | `postgres://user:pass@db:5432/charityos` | Database connection string |
| `CELERY_BROKER_URL` | `redis://redis:6379/0` | Redis URL for Celery |
| `DEFAULT_FROM_EMAIL` | `noreply@charityos.co.tz` | System email sender |
| `EMAIL_HOST` | `smtp.gmail.com` | SMTP server for outbound email |

---


