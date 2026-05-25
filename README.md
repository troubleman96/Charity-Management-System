# CharityOS 🌍: The Super Detailed Master Guide

CharityOS is a comprehensive, full-stack SaaS platform built specifically to empower non-profit organizations managing orphan support programs. It provides a transparent, efficient, and scalable way to connect donors directly with the children they support, manage operations, and ensure every donation is tracked from receipt to allocation.

---

## 🎯 Purpose & Scope
The goal of CharityOS is to replace fragmented spreadsheets and legacy systems with a modern, secure, role-based web application. It handles:
- **Donor Management & Engagement**: Donor portals with full visibility into their impact.
- **Beneficiary Lifecycle**: Tracking orphans, their education, health, and specific assistance needs.
- **Financial Transparency**: End-to-end tracking of cash and in-kind donations, automated PDF receipts, and strict fund allocation logs.
- **Internal Operations**: Streamlining staff communication, audit trails for security, and automated report generation.

---

## 🏗️ Technical Architecture
CharityOS is built on a robust, proven stack prioritizing security, maintainability, and performance over bleeding-edge complexity.

* **Backend Framework**: Django 4.2+ (Python 3.10+)
* **Database Engine**: PostgreSQL (Production) / SQLite (Development)
* **Background Processing**: Celery with Redis broker (for PDFs, emails, and cron jobs)
* **Frontend Paradigm**: Server-Side Rendered (SSR) Django Templates + Vanilla CSS + HTMX 
* **Authentication**: Django Auth extended with strict Role-Based Access Control (RBAC) via Mixins and Custom Email/Username Backend.

### Why Vanilla CSS & HTMX?
Instead of relying on heavy pipelines like Tailwind or React, the UI is built using a custom, modular Vanilla CSS design system (`static/css/components/`). This keeps the repository lightweight, easily readable, and heavily inspired by modern SaaS aesthetics without the build-step overhead.

---

## 🗄️ Master ERD & Data Flow

CharityOS uses a strictly normalized database to ensure data integrity.

```text
User (Django Auth)
  │
  ├─ 1:1 ─ UserProfile (Role: admin, staff, donor)
  │
  └─ 1:1 (If Donor) ─ Donor (Organization, Preferences)
                        │
                        ├─ 1:N ─ Donation (Cash/In-Kind) ─ 1:N ─ DonationAllocation
                        │                                             │
                        └─ M:N ─ DonorBeneficiaryLink                 │
                                      │                               │
                                      └─ M:1 ─ Beneficiary ─ 1:N ─ AssistanceRequest
                                                    │
                                                    └─ 1:N ─ ProgressUpdate
```

---

## 📂 System Modules (Apps) Deep Dive

### 1. Core App (`apps/core/`)
> System-wide infrastructure: audit logging, role-based access control, template utilities, and dashboard routing.

The `core` app does NOT manage business entities. It provides the foundational plumbing that every other app depends on.

**`AuditLog` — Immutable System-Wide Event Tracker**
Every significant action in the system generates an `AuditLog` entry. This model uses Django's `ContentType` framework to create a `GenericForeignKey`, meaning it can be attached to ANY model instance in the entire system without explicit foreign keys. Tracks: `user`, `content_object`, `action` (CREATE, UPDATE, LOGIN), and `ip_address`.

**Security Enforcement Mixins:**
Every class-based view MUST inherit from one:
- `AdminRequiredMixin`: Reports, system config, user management.
- `StaffRequiredMixin`: Beneficiary CRUD, donation recording.
- `DonorRequiredMixin`: Donor portal views.

### 2. Accounts App (`apps/accounts/`)
> User authentication, registration, profile management, and the UserProfile extension model.

**`UserProfile` — Extended User Data**
CharityOS uses a `OneToOne` profile extension instead of a Custom User Model for simplicity. It adds `role`, `phone`, and `avatar`.

**Custom Authentication Backend (`EmailOrUsernameBackend`)**
Allows users to log in with either their email address or their username via a custom backend registered in `settings/base.py`.

**Signals:**
Connected to the `User` model's `post_save` event. Automatically creates a `UserProfile` for every new `User`. By default, superusers get the `admin` role, and standard registrations get the `donor` role.

### 3. Beneficiaries App (`apps/beneficiaries/`)
> The heart of CharityOS. Manages orphan profiles, assistance needs, progress tracking, and donor sponsorship links.

**`Beneficiary` — Orphan Profile**
Automatically generates a unique `beneficiary_code` (`BEN-YYYY-NNNN`) on first save. Tracks health status, education, guardian details, and system status (active, inactive, graduated).

**`AssistanceRequest` — Needs Tracking**
Represents a specific financial or material need for a child. Staff submit these; admins approve them; donations fund them. Status lifecycle: `pending` → `approved` → `fulfilled` (when fully funded by a `DonationAllocation`).

**Data Flow: From Need to Funding**
1. Staff creates an `AssistanceRequest` (status: pending).
2. Admin reviews and approves (status: approved).
3. Staff creates a `DonationAllocation` linking a Donation to the request.
4. `AssistanceRequest` status updated to "fulfilled" when fully funded.

### 4. Donations App (`apps/donations/`)
> Financial tracking engine: logs cash and in-kind contributions, manages fund allocation, and generates PDF receipts asynchronously.

**Key Design Principle:** Donations are immutable ledger entries. Once logged, they cannot be silently deleted. They can only be allocated.

**`Donation` — Core Ledger Entry**
Supports two types: `cash` (with amount and payment method) and `in_kind` (with description and estimated value).
Status Lifecycle (auto-managed by allocations): `received` → `partial` → `allocated`.

**`DonationAllocation` — Fund Distribution**
Maps exactly WHERE a donation's cash was spent. Links a `Donation` to a `Beneficiary` and optionally to a specific `AssistanceRequest`.

**Celery Tasks (`tasks.py`)**
- `send_donation_receipt(donation_id)`: Renders HTML receipt → WeasyPrint PDF → saves to `DonationReceipt` → emails to donor.
- `check_low_funds()`: Nightly job that sums unallocated cash and creates admin Notifications if below the threshold.

### 5. Donors App (`apps/donors/`)
> Dedicated portal views for external sponsors to see their impact.

**`Donor` Profile**
Holds specific donor preferences (e.g., `is_anonymous`, `tax_receipt_required`). Provides helper methods like `get_total_donated()`.

**Dashboard Views:**
Donors do not see the administrative dashboards. Their dashboard provides a read-only view of their lifetime contributions, a list of their sponsored children (`DonorBeneficiaryLink`), and recent progress updates.

### 6. Communications App (`apps/communications/`)
> Internal staff messaging, automated system alerts, and outbound email logging.

- **`Notification`**: In-app alerts for users (e.g., "Donation Received", "Request Approved").
- **`Message`**: Internal direct messages between staff/admin users.
- **`EmailLog`**: Audit log of all outbound emails sent by the system (via Celery), tracking delivery status (`pending`, `sent`, `failed`) and error messages.

---

## 🚀 Getting Started (Development & Deployment)

### Setup Steps
1. **Clone & Virtual Environment**
   ```bash
   git clone <repo-url>
   cd Charity-Management-System/charity_cms
   python3 -m venv venv
   source venv/bin/activate
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Database Migrations**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

4. **Create Admin Superuser**
   ```bash
   # Will automatically be assigned the 'admin' role by the signals!
   python manage.py createsuperuser
   ```

5. **Run the Development Server**
   ```bash
   python manage.py runserver
   ```
   *Access the site at `http://localhost:8000/`*

6. **Run Celery Worker (In a separate terminal)**
   ```bash
   source venv/bin/activate
   celery -A config worker -l info
   ```

### 🐳 Docker (Production / Staging)
A complete `Dockerfile` and `docker-compose.yml` are provided in the root directory for easy deployment.

```bash
# Build and start the Postgres, Redis, Django Web, and Celery containers
docker-compose up --build -d

# Apply migrations inside the container
docker-compose exec web python manage.py migrate

# Create superuser
docker-compose exec web python manage.py createsuperuser
```
