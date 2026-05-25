# CharityOS 🌍

CharityOS is a comprehensive, full-stack SaaS platform built specifically to empower non-profit organizations managing orphan support programs in Tanzania. It provides a transparent, efficient, and scalable way to connect donors directly with the children they support, manage operations, and ensure every donation is tracked from receipt to allocation.

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
* **Frontend Paradigm**: Server-Side Rendered (SSR) Django Templates + Vanilla CSS + HTMX (No heavy JS frameworks)
* **Authentication**: Django Auth extended with strict Role-Based Access Control (RBAC) via Mixins.

### Why Vanilla CSS & HTMX?
Instead of relying on heavy pipelines like Tailwind or React, the UI is built using a custom, modular Vanilla CSS design system (`static/css/components/`). This keeps the repository extremely lightweight, easily readable, and heavily inspired by modern SaaS aesthetics without the build-step overhead. HTMX is sprinkled in for dynamic partial reloads (e.g., filtering tables) without page refreshes.

---

## 📚 Documentation Directory
To maintain a clean repository, detailed technical documentation has been separated into specific files. Please refer to the `docs/` folder and individual app READMEs for deep dives:

### Core Documentation
* 📖 [**Architecture Overview**](docs/architecture/overview.md) - Deep dive into request lifecycles, Celery background jobs, and RBAC implementation.
* 🗄️ [**Data Models & ERD**](docs/architecture/data_models.md) - Explains all database relationships, the User extension paradigm, and financial allocation schemas.
* 🎨 [**UI Reference HTML**](docs/charity_cms_saas_dashboard.html) - The original static HTML/CSS prototype that the Django templates are based on.

### App-Specific Guides
Every Django app in `charity_cms/apps/` contains its own `README.md` explaining its specific responsibilities and logic:
- [`apps/core/README.md`](charity_cms/apps/core/README.md) - Audit logs, mixins, templatetags.
- [`apps/accounts/README.md`](charity_cms/apps/accounts/README.md) - Auth, roles, profiles.
- [`apps/beneficiaries/README.md`](charity_cms/apps/beneficiaries/README.md) - Orphans, assistance requests, progress updates.
- [`apps/donations/README.md`](charity_cms/apps/donations/README.md) - Cash/In-kind tracking, Celery PDF receipts.
- [`apps/donors/README.md`](charity_cms/apps/donors/README.md) - Donor dashboards and analytics.
- [`apps/communications/README.md`](charity_cms/apps/communications/README.md) - Internal staff messaging and email logs.
- [`apps/reports/README.md`](charity_cms/apps/reports/README.md) - Automated PDF report generators.

---

## 🚀 Getting Started (Development)

### Prerequisites
- Python 3.10+
- Redis (for Celery workers)

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

---

## 🐳 Docker (Production / Staging)
A complete `Dockerfile` and `docker-compose.yml` are provided in the root directory for easy deployment.

```bash
# Build and start the Postgres, Redis, Django Web, and Celery containers
docker-compose up --build -d

# Apply migrations inside the container
docker-compose exec web python manage.py migrate

# Create superuser
docker-compose exec web python manage.py createsuperuser
```

---

## 🛡️ Security & Auditing
CharityOS treats data integrity with the highest priority:
1. **AuditLog**: Every critical view (e.g., adding a donation, updating a beneficiary status) explicitly calls `log_action()` to create an immutable record in the `core_auditlog` table, recording the user, action, and IP address.
2. **Strict RBAC**: Every class-based view inherits from `AdminRequiredMixin`, `StaffRequiredMixin`, or `DonorRequiredMixin`. A staff member can never access a view reserved for donors, and vice-versa.

---
*Built for impact. Developed with ❤️.*
