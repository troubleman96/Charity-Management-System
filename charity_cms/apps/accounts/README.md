# Accounts App (`apps/accounts/`)

> User authentication, registration, profile management, and the UserProfile extension model.

---

## 📁 File Structure
```
apps/accounts/
├── __init__.py
├── apps.py             ← App config (registers signals)
├── models.py           ← UserProfile model (OneToOne → User)
├── signals.py          ← Auto-creates UserProfile on User creation
├── forms.py            ← Login, registration, and profile forms
├── views.py            ← Login, logout, register, profile views
├── urls.py             ← /accounts/ routes
├── admin.py            ← Django admin registration
└── README.md           ← THIS FILE
```

---

## Concept: Why Not a Custom User Model?
Django offers two ways to extend the User:
1. **Custom User Model** — Replace `User` entirely (complex, requires migration from scratch).
2. **OneToOne Profile** — Keep the default `User` and add a linked `UserProfile` for extra fields.

CharityOS uses option 2 because:
- It's simpler and less error-prone.
- Django's built-in admin, permissions, and third-party libraries work out of the box.
- The role system (`admin`/`staff`/`donor`) is cleanly separated from auth credentials.

---

## Models

### `UserProfile` — Extended User Data
Auto-created for every `User` via the `post_save` signal.

| Field | Type | Constraints | Description |
|-------|------|------------|-------------|
| `user` | OneToOneField → `auth.User` | CASCADE, `related_name='profile'` | The Django auth user this extends |
| `role` | CharField(20) | choices: `admin`, `staff`, `donor` | Determines dashboard and feature access |
| `phone` | CharField(20) | blank=True | Contact phone (e.g., +255712345678) |
| `avatar` | ImageField | blank=True, uploads to `avatars/` | Profile picture |
| `created_at` | DateTimeField | auto_now_add | Record creation timestamp |
| `updated_at` | DateTimeField | auto_now | Last modification timestamp |

**Indexes:** `role` field is indexed for fast filtering.

**Helper Properties:**
- `is_admin` → `self.role == 'admin'`
- `is_staff_member` → `self.role == 'staff'`
- `is_donor` → `self.role == 'donor'`

**How to access from a User:**
```python
user = request.user
role = user.profile.role         # 'admin', 'staff', or 'donor'
phone = user.profile.phone       # '+255712345678'
```

---

## Signals (`signals.py`)

Two signals are connected to the `User` model's `post_save` event:

1. **`create_user_profile`** — When a new `User` is created (`created=True`), automatically creates a blank `UserProfile` with default role `donor`.
2. **`save_user_profile`** — When a `User` is saved, also saves its linked `UserProfile`.

**Why?** This ensures every User ALWAYS has a UserProfile. Without this, accessing `user.profile` would crash with a `RelatedObjectDoesNotExist` error.

---

## Forms (`forms.py`)

| Form | Fields | Usage |
|------|--------|-------|
| `CustomUserCreationForm` | `username`, `email`, `first_name`, `last_name`, `password1`, `password2` | Standard Django registration with extra name fields |
| `UserProfileForm` | `phone`, `avatar` | Profile update page |
| `DonorRegistrationForm` | Combined user + profile + donor fields | Public donor self-registration |

**`DonorRegistrationForm` workflow:**
1. Creates the `User` record.
2. The signal creates the `UserProfile` (role defaults to `donor`).
3. The form's `save()` method creates the `Donor` record in the `donors` app.
4. All three records are created in a single database transaction.

---

## Views (`views.py`)

| View | URL | Auth | Description |
|------|-----|------|-------------|
| `CustomLoginView` | `/accounts/login/` | Public | Login form, writes AuditLog on success (tracks IP) |
| `CustomLogoutView` | `/accounts/logout/` | Auth | Destroys session, redirects to login |
| `DonorRegistrationView` | `/accounts/register/` | Public | Donor self-registration using `DonorRegistrationForm` |
| `ProfileView` | `/accounts/profile/` | Auth | View/edit profile using `UserProfileForm` |

---

## Templates Used
- `templates/accounts/login.html` — Dark-themed login form with CSS classes from the design system.
- `templates/accounts/register.html` — Multi-section registration form (Personal Info → Contact).
- `templates/accounts/profile.html` — Profile view/edit page.

---

## Implementation Status

| Component | Status |
|-----------|--------|
| UserProfile model | ✅ Complete |
| Post-save signal (auto-create profile) | ✅ Complete |
| Email/username login backend | ✅ Complete |
| Login / logout / register views | ✅ Complete |
| Profile view/edit | ✅ Complete |
| All templates | ✅ Complete |
| Django admin (inline profile editing) | ✅ Complete |

## Seed Users

Use the `seed_users` management command (in the `core` app) to create test accounts for all roles:

```bash
python manage.py seed_users
```

See `apps/core/README.md` for credentials.
