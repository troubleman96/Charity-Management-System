# Beneficiaries App (`apps/beneficiaries/`)

> The heart of CharityOS. Manages orphan profiles, assistance needs, progress tracking, and donor sponsorship links.

---

## 📁 File Structure
```
apps/beneficiaries/
├── __init__.py
├── apps.py             ← App config
├── models.py           ← Beneficiary, AssistanceRequest, BeneficiaryUpdate, DonorBeneficiaryLink
├── forms.py            ← CRUD forms for beneficiaries and requests
├── views.py            ← List, detail, create, update views (all StaffRequiredMixin)
├── urls.py             ← /beneficiaries/ routes
├── admin.py            ← Django admin registration with inline models
└── README.md           ← THIS FILE
```

---

## Models

### `Beneficiary` — Orphan Profile (21 fields)
The central entity. Automatically generates a unique `beneficiary_code` on first save.

| Field | Type | Constraints | Description |
|-------|------|------------|-------------|
| `beneficiary_code` | CharField(20) | unique, auto-generated, editable=False | Format: `BEN-YYYY-NNNN` (e.g., `BEN-2025-0014`) |
| `first_name` | CharField(100) | required | Child's first name |
| `last_name` | CharField(100) | required | Child's last name |
| `date_of_birth` | DateField | required | Used to compute `age` property |
| `gender` | CharField(10) | choices: `male`, `female` | Biological sex |
| `photo` | ImageField | blank, uploads to `beneficiaries/` | Child's photo for profiles and updates |
| `school_name` | CharField(200) | blank | Name of school currently attending |
| `school_grade` | CharField(50) | blank | Current grade/class level |
| `health_status` | TextField | blank | Medical conditions, notes, or "Healthy" |
| `guardian_name` | CharField(200) | blank | Name of the child's guardian |
| `guardian_phone` | CharField(20) | blank | Guardian's phone number |
| `guardian_relationship` | CharField(50) | blank | e.g., "Aunt", "Uncle", "Grandmother" |
| `location_region` | CharField(100) | blank | Tanzania region (e.g., "Dar es Salaam") |
| `location_district` | CharField(100) | blank | Specific district/ward |
| `date_enrolled` | DateField | required | When the child entered the program |
| `status` | CharField(20) | choices: `active`, `inactive`, `graduated` | Current program status |
| `notes` | TextField | blank | Internal admin/staff notes |
| `registered_by` | FK → `auth.User` | SET_NULL | Staff member who registered the child |
| `created_at` | DateTimeField | auto_now_add | Record creation time |
| `updated_at` | DateTimeField | auto_now | Last modification time |

**Auto-generated code logic (`save()`):**
```python
def save(self, *args, **kwargs):
    if not self.beneficiary_code:
        year = date.today().year
        count = Beneficiary.objects.filter(beneficiary_code__startswith=f'BEN-{year}').count()
        self.beneficiary_code = f'BEN-{year}-{str(count + 1).zfill(4)}'
    super().save(*args, **kwargs)
```

**Status Lifecycle:**
```
active → inactive   (admin deactivates, e.g., child relocated)
active → graduated  (aged out or completed program)
inactive → active   (re-enrolled)
```

---

### `AssistanceRequest` — Needs Tracking (12 fields)
Represents a specific financial or material need for a child. Staff submit these; admins approve them; donations fund them.

| Field | Type | Constraints | Description |
|-------|------|------------|-------------|
| `request_ref` | CharField(30) | unique, auto-generated | Format: `REQ-YYYY-NNNN` |
| `beneficiary` | FK → `Beneficiary` | CASCADE | The child this need is for |
| `requested_by` | FK → `auth.User` | SET_NULL | Staff who submitted the request |
| `request_type` | CharField(50) | choices | `education`, `food`, `medical`, `clothing`, `other` |
| `description` | TextField | required | Detailed description of the need |
| `estimated_cost` | DecimalField(12,2) | nullable | Estimated cost in TZS |
| `status` | CharField(20) | choices, default=`pending` | Workflow status |
| `reviewed_by` | FK → `auth.User` | SET_NULL, nullable | Admin who approved/rejected |
| `review_notes` | TextField | blank | Admin's notes on the decision |
| `created_at` | DateTimeField | auto_now_add | When the request was submitted |
| `updated_at` | DateTimeField | auto_now | Last modification |

**Status Lifecycle:**
```
pending → approved   (admin approves, ready for funding)
pending → rejected   (admin rejects with notes)
approved → fulfilled (funds fully allocated via DonationAllocation)
```

---

### `DonorBeneficiaryLink` — Sponsorship Mapping
Connects a `Donor` to a `Beneficiary` they sponsor. Many-to-many through table.

| Field | Type | Description |
|-------|------|-------------|
| `donor` | FK → `Donor` | The sponsoring donor |
| `beneficiary` | FK → `Beneficiary` | The sponsored child |
| `start_date` | DateField | When sponsorship started |
| `end_date` | DateField (nullable) | NULL = still active |
| `is_active` | BooleanField | Quick filter for active sponsorships |
| `notes` | TextField | Internal notes about the sponsorship |

**Unique constraint:** `(donor, beneficiary)` — a donor can only sponsor a child once.

---

### `BeneficiaryUpdate` — Progress Journal
Staff write narrative updates about a child's progress. These are visible to linked donors in their portal.

| Field | Type | Description |
|-------|------|-------------|
| `beneficiary` | FK → `Beneficiary` | The child this update is about |
| `title` | CharField(200) | Headline (e.g., "Term 2 Exam Results") |
| `content` | TextField | Narrative body for donors to read |
| `photo` | ImageField | Optional photo showing progress |
| `created_by` | FK → `auth.User` | Staff who wrote the update |
| `notified_donors` | BooleanField | Whether linked donors have been notified |
| `created_at` | DateTimeField | When the update was written |

---

## Views

| View | URL | Description |
|------|-----|-------------|
| `BeneficiaryListView` | `/beneficiaries/` | Paginated list with search, filter by status/region |
| `BeneficiaryDetailView` | `/beneficiaries/<pk>/` | Full child profile: sponsors, needs, updates |
| `BeneficiaryCreateView` | `/beneficiaries/create/` | Multi-section form (personal, education, guardian) |
| `BeneficiaryUpdateView` | `/beneficiaries/<pk>/edit/` | Edit existing child record |
| `AssistanceRequestCreateView` | `/beneficiaries/requests/create/` | Submit a new need for a child |
| `ProgressUpdateCreateView` | `/beneficiaries/updates/create/` | Log a progress update for a child |

---

## Data Flow: From Need to Funding

```
1. Staff creates an AssistanceRequest (status: pending)
   ↓
2. Admin reviews and approves (status: approved)
   ↓
3. Staff creates a DonationAllocation linking a Donation to the AssistanceRequest
   ↓
4. DonationAllocation.save() updates Donation.status (received → partial → allocated)
   ↓
5. AssistanceRequest status updated to "fulfilled" when fully funded
```
