# Core App

The `core` application acts as the foundational layer for CharityOS. It does not manage specific business entities (like orphans or donations), but rather provides infrastructure, security, and shared utilities utilized by all other apps.

## Responsibilities
1. **Audit Logging**: Maintains the `AuditLog` model to track who did what, when, and from where.
2. **Access Control**: Houses the RBAC Mixins used by all views to secure the application.
3. **Template Utilities**: Provides custom template tags for the frontend UI.
4. **Dashboards**: Routes authenticated users to their respective dashboards based on their role.

## Key Components

### Models
- **`AuditLog`**: Uses Django's `ContentType` to form a `GenericForeignKey`, allowing an audit log entry to be attached to *any* model instance in the system.

### Mixins (`mixins.py`)
These are critical for security. Every class-based view in the system MUST inherit from one of these:
- `RoleRequiredMixin`: Base class checking `UserProfile.role`.
- `AdminRequiredMixin`: Restricts to `role == 'admin'`.
- `StaffRequiredMixin`: Restricts to `role in ['admin', 'staff']`.
- `DonorRequiredMixin`: Restricts to `role == 'donor'`.

### Utils (`utils.py`)
- `log_action(user, content_object, action, changes=None, ip_address=None)`: The standard function called in `form_valid()` methods across the app to write an `AuditLog` entry.

### Template Tags (`templatetags/charity_tags.py`)
- `status_color`: Converts a database status string (e.g., `fully_allocated`) into a CSS class suffix (`success`, `warn`, `error`) to style badges in the UI.
- `currency`: Formats integer amounts into human-readable TZS strings (e.g., `10000` -> `TZS 10,000`).
