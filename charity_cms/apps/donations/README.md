# Donations App (`apps/donations/`)

> Financial tracking: logs cash/in-kind contributions, manages fund allocation, generates PDF receipts via Celery.

## 📁 File Structure
```
apps/donations/
├── models.py    ← Donation, DonationReceipt, DonationAllocation
├── forms.py     ← Donation entry forms with conditional fields
├── views.py     ← CRUD views (StaffRequiredMixin)
├── tasks.py     ← Celery async tasks (PDF receipt, low-fund alerts)
├── urls.py      ← /donations/ routes
├── admin.py     ← Django admin with inline allocations
└── README.md    ← THIS FILE
```

## Key Design Principle
> Donations are immutable ledger entries. Once logged, they cannot be deleted — only allocated.

## Models

### `Donation` — Core Ledger (16 fields)
| Field | Type | Description |
|-------|------|-------------|
| `donation_ref` | CharField(30), auto | `DON-YYYY-NNNNN` |
| `donor` | FK → Donor, nullable | NULL = anonymous |
| `donation_type` | choices | `cash` or `in_kind` |
| `amount` | DecimalField | Cash amount in TZS |
| `payment_method` | choices | `cash`, `mpesa`, `tigopesa`, `bank`, `other` |
| `transaction_reference` | CharField | M-Pesa/bank ref number |
| `in_kind_description` | TextField | Items donated (in-kind only) |
| `in_kind_estimated_value` | DecimalField | Estimated value |
| `donation_date` | DateField | Date received |
| `purpose` | CharField | Fund designation |
| `status` | choices | `received` → `partial` → `allocated` |
| `recorded_by` | FK → User | Staff who logged it |

**Computed:** `allocated_amount`, `remaining_amount`

**Status auto-updates via `DonationAllocation.save()`:**
```
received → partial   (first allocation, funds remain)
partial → allocated  (remaining reaches 0)
```

### `DonationReceipt` — PDF Record
| Field | Type | Description |
|-------|------|-------------|
| `donation` | OneToOne → Donation | Source donation |
| `receipt_number` | CharField | Unique receipt ID |
| `pdf_file` | FileField | Generated PDF |
| `email_status` | choices | `pending`, `sent`, `failed` |

### `DonationAllocation` — Fund Distribution
| Field | Type | Description |
|-------|------|-------------|
| `donation` | FK → Donation | Source of funds |
| `beneficiary` | FK → Beneficiary | Recipient child |
| `assistance_request` | FK → AssistanceRequest | Specific need funded |
| `amount` | DecimalField | Amount in TZS |
| `allocation_type` | choices | `education`, `food`, `medical`, `clothing`, `general` |
| `allocated_by` | FK → User | Who made the allocation |

**Side effect:** `save()` auto-updates parent `Donation.status`.

## Celery Tasks (`tasks.py`)

### `send_donation_receipt(donation_id)`
1. Fetches Donation → renders HTML receipt → WeasyPrint PDF → emails to donor → updates `email_status`.

### `check_low_funds()`
Nightly cron: sums unallocated cash; creates admin Notification if below threshold.

## Views
| View | URL | Description |
|------|-----|-------------|
| `DonationListView` | `/donations/` | Paginated, filterable by type/status |
| `DonationCreateView` | `/donations/create/` | JS toggles cash vs in-kind fields |
| `DonationDetailView` | `/donations/<pk>/` | Detail with allocation history |
