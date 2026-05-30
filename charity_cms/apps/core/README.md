# core — Shared Infrastructure

> **Status: Fully Implemented** — All models, views, utilities, and management commands are complete.

---

# Core App (`apps/core/`)

> System-wide infrastructure: audit logging, role-based access control, template utilities, and dashboard routing.

The `core` app does NOT manage business entities. It provides the foundational plumbing that every other app depends on.

---

## 📁 File Structure
```
apps/core/
├── __init__.py
├── models.py           ← AuditLog model (GenericForeignKey-based)
├── mixins.py           ← RBAC security mixins (AdminRequired, StaffRequired, DonorRequired)
├── utils.py            ← log_action() helper function
├── views.py            ← Landing page, role-based dashboard redirect
├── urls.py             ← Root routes: /, /dashboard/
├── admin_urls.py       ← Admin panel routes: /admin-panel/
├── staff_urls.py       ← Staff panel routes: /staff/
├── admin.py            ← Django admin registration for AuditLog
├── context_processors.py ← Injects global variables into all templates
├── templatetags/
│   └── charity_tags.py ← Custom filters: |status_color, |currency
└── README.md           ← THIS FILE
```

---

## Models

### `AuditLog` — Immutable System-Wide Event Tracker
Every significant action in the system (login, donation creation, beneficiary update, etc.) generates an `AuditLog` entry. This model uses Django's `ContentType` framework to create a `GenericForeignKey`, meaning it can be attached to ANY model instance in the entire system without explicit foreign keys.

| Field | Type | Description |
|-------|------|-------------|
| `user` | ForeignKey → `auth.User` | Who performed the action |
| `content_type` | ForeignKey → `ContentType` | Which model was affected (e.g., `Donation`) |
| `object_id` | PositiveIntegerField | Primary key of the affected record |
| `content_object` | GenericForeignKey | Resolved reference to the actual object |
| `action` | CharField | Action type: `CREATE`, `UPDATE`, `DELETE`, `LOGIN`, `LOGOUT` |
| `changes` | JSONField | Diff of what changed (optional) |
| `ip_address` | GenericIPAddressField | IP of the user who made the change |
| `created_at` | DateTimeField | When the event occurred |

**Why GenericForeignKey?** It avoids creating separate audit tables for every model. One table tracks changes to Donations, Beneficiaries, Users — everything.

---

## Mixins (`mixins.py`) — Security Enforcement

These mixins are the backbone of CharityOS security. Every class-based view MUST inherit from one:

| Mixin | Allowed Roles | Use Case |
|-------|--------------|----------|
| `RoleRequiredMixin` | (Base class) | Never used directly |
| `AdminRequiredMixin` | `admin` | Reports, system config, user management |
| `StaffRequiredMixin` | `admin`, `staff` | Beneficiary CRUD, donation recording |
| `DonorRequiredMixin` | `donor` | Donor portal views |

**How it works:**
1. The mixin checks `request.user.is_authenticated`.
2. If authenticated, it checks `request.user.profile.role` against the allowed roles.
3. If unauthorized, it redirects to the login page with an error message.

```python
# Example usage in any view:
class BeneficiaryCreateView(StaffRequiredMixin, CreateView):
    model = Beneficiary
    # Only admin and staff can reach this view
```

---

## Utils (`utils.py`)

### `log_action(user, content_object, action, changes=None, ip_address=None)`
The standard function for creating audit entries. Called in `form_valid()` methods across every app.

```python
# Example: Logging a new donation
from apps.core.utils import log_action

def form_valid(self, form):
    donation = form.save(commit=False)
    donation.recorded_by = self.request.user
    donation.save()
    log_action(
        user=self.request.user,
        content_object=donation,
        action='CREATE',
        ip_address=self.request.META.get('REMOTE_ADDR')
    )
    return super().form_valid(form)
```

---

## Template Tags (`templatetags/charity_tags.py`)

Custom Django template filters used throughout every template:

| Filter | Input | Output | Usage |
|--------|-------|--------|-------|
| `status_color` | `"active"` | `"success"` | Maps status strings to CSS badge classes |
| `status_color` | `"pending"` | `"warn"` | Used like: `{{ obj.status\|status_color }}` |
| `status_color` | `"rejected"` | `"error"` | Applied to `<span class="badge badge-{{ val }}">` |
| `currency` | `10000` | `"TZS 10,000"` | Formats numbers as Tanzanian Shilling strings |

---

## Context Processors (`context_processors.py`)

Injects variables into EVERY template without passing them manually:
- `branding`: Application name, tagline
- `unread_notifications_count`: Count of unread notifications for the current user
- `current_year`: For footer copyright

---

## Views (`views.py`)

| View | URL | Description |
|------|-----|-------------|
| `LandingPageView` | `/` | Public landing page (no auth required) |
| `DashboardRedirectView` | `/dashboard/` | Checks user role, redirects to the correct dashboard |
| `AdminDashboardView` | `/admin-panel/` | Admin KPIs: total donations, beneficiaries, pending requests, charts |
| `StaffDashboardView` | `/staff/` | Staff quick actions and pending items |

---

## Seed Users Management Command

Creates demo accounts for testing every role without manual setup:

```bash
python manage.py seed_users           # Create demo users
python manage.py seed_users --reset   # Delete and recreate all
python manage.py seed_users --quiet   # No terminal output
```

| Role      | Username    | Password  | Email                  |
|-----------|-------------|-----------|------------------------|
| admin     | admin_demo  | Admin@123 | admin@charityos.demo   |
| staff     | staff_demo  | Staff@123 | staff@charityos.demo   |
| donor     | donor_demo  | Donor@123 | donor@charityos.demo   |
| superuser | superadmin  | Super@123 | super@charityos.demo   |

---

## Implementation Status

| Component | Status |
|-----------|--------|
| AuditLog model | ✅ Complete |
| RBAC mixins & decorator | ✅ Complete |
| Admin dashboard (KPIs + Chart.js) | ✅ Complete |
| Staff dashboard | ✅ Complete |
| Context processor | ✅ Complete |
| Template tags (`status_color`, `currency`, `initials`) | ✅ Complete |
| `log_action()` utility | ✅ Complete |
| `seed_users` management command | ✅ Complete |
| Landing page | ✅ Complete |
