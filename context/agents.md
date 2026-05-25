# CharityOS Context Guide for Agents

## Overview
CharityOS is a comprehensive, full-stack Django SaaS platform tailored for non-profit organizations, specifically targeting orphan support in Tanzania. The application connects donors directly with the children they support, ensuring transparency, operational efficiency, and scalable growth.

## Architecture
- **Backend Framework:** Django (Python 3.10+)
- **Database:** PostgreSQL (Production), SQLite (Development)
- **Task Queue:** Celery with Redis broker
- **Frontend Paradigm:** Server-Side Rendered (SSR) with Django Templates + Vanilla CSS + HTMX for dynamic interactions. No heavy JS frameworks (React/Vue) are used.
- **Styling:** Dark-themed SaaS UI built with a custom component library (`static/css/components/`).

## Core Applications
1. **`core`:** Handles RBAC (Role-Based Access Control), Audit Logs, base models, template tags, and dashboards.
2. **`accounts`:** Extends Django auth with `UserProfile` (Admin, Staff, Donor) and handles login/registration.
3. **`beneficiaries`:** Manages the lifecycle of enrolled orphans, assistance requests (needs), and progress updates.
4. **`donations`:** Logs incoming cash and in-kind contributions, handles fund allocation, and generates digital receipts (via Celery & WeasyPrint).
5. **`communications`:** Internal messaging between staff/admins and system notifications.
6. **`reports`:** PDF generation for monthly summaries and donor directories.

## Development Principles
- **RBAC Enforcement:** Never expose a view without the proper Mixin (`AdminRequiredMixin`, `StaffRequiredMixin`, `DonorRequiredMixin`).
- **Audit Trails:** Use `apps.core.utils.log_action` to track significant state changes across the system.
- **Modular CSS:** Always add new styles to their specific component files in `static/css/components/` and import them in `main.css`. Avoid inline styles.
- **Background Tasks:** Any heavy I/O operation (PDF generation, bulk email) MUST be offloaded to Celery.

## Quick Start
```bash
python manage.py runserver
celery -A config worker -l info
```
