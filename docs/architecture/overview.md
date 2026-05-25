# CharityOS Architectural Overview

## System Architecture
CharityOS follows a classic, robust Monolithic architecture built on Django. The decision to use a monolith over microservices was made to maximize development speed, maintainability, and operational simplicity for the NGO.

### Request-Response Lifecycle
1. **Client Request**: A user requests a URL (e.g., `/donations/list/`).
2. **Django Router**: `config/urls.py` routes the request to the `donations` app.
3. **Middleware**:
   - `AuthenticationMiddleware`: Identifies the user.
   - Security Middlewares: CSRF protection, Clickjacking prevention.
4. **View Execution**: The view (e.g., `DonationListView`) is protected by `StaffRequiredMixin`. If the user is authorized, the view queries the database.
5. **Template Rendering**: The view passes context data to the template engine. The template inherits from `base.html` and renders HTML using Vanilla CSS components.
6. **Response**: Pure HTML is sent back to the browser. HTMX may intercept links/forms to swap specific DOM elements instead of full page reloads.

## Background Processing (Celery)
Synchronous execution of heavy tasks (like PDF generation and sending mass emails) blocks the web server, leading to poor user experience. CharityOS solves this by offloading these tasks to Celery.

- **Broker**: Redis serves as the message broker, queuing tasks.
- **Worker**: `celery -A config worker` runs as a separate process, picking up tasks from Redis.
- **Beat (Cron)**: `django-celery-beat` is used for scheduled tasks (e.g., running `check_low_funds` every night at midnight).

### Example Workflow: Donation Receipt
1. Staff records a `cash` donation in the Django UI.
2. The `Donation.save()` method triggers.
3. A Celery task `send_donation_receipt.delay(donation_id)` is pushed to Redis.
4. The web response returns immediately to the staff member (UI is fast).
5. The Celery worker picks up the task, uses `WeasyPrint` to generate a PDF, attaches it to an email, and sends it to the donor.

## Role-Based Access Control (RBAC)
Instead of using Django's complex Groups/Permissions framework, CharityOS uses a streamlined, strict role definition via the `UserProfile.role` field:
- **`admin`**: Full access to all dashboards, configuration, and reports.
- **`staff`**: Access to manage beneficiaries and donations, but no access to system config or global financial reports.
- **`donor`**: Restricted to the Donor Portal. Can ONLY see their own profile, their own donations, and the beneficiaries directly linked to them.

Views enforce this via custom mixins in `apps.core.mixins`:
```python
class DonationCreateView(StaffRequiredMixin, CreateView):
    # Only staff/admins can execute this
```

## CSS & Frontend Paradigm
CharityOS completely avoids npm, Webpack, React, Vue, or Tailwind.
- **Why?** To ensure the project can be maintained by developers familiar with standard HTML/CSS without needing to manage complex build pipelines.
- **How?** `static/css/base.css` defines CSS Variables (Custom Properties) for themes. `static/css/components/*.css` defines isolated styles for specific UI elements (Cards, Tables, Badges).
- **HTMX**: Used for dynamic interactions (like filtering the beneficiary list) by sending an AJAX request and replacing a specific `<div>` with the HTML response from Django.
