# Data Flow Models
## Charity Management System
---

## DFD Level 0 — Context Diagram

```
                    ┌─────────────────────────────┐
                    │                             │
  [DONOR] ─────────►│   CHARITY MANAGEMENT SYSTEM │◄──────── [ADMIN]
          ◄─────────│                             │──────────►
                    │      (Django Web App)        │
  [STAFF] ─────────►│                             │◄──────── [PUBLIC]
          ◄─────────│                             │
                    └─────────────────────────────┘
                                  │ ▲
                                  ▼ │
                         [EMAIL / SMS SERVICE]
                         (Celery + SMTP/AT API)
```

**External Entities:**
- **Donor** — Registers, donates, views receipts & beneficiary updates
- **Admin** — Full system oversight, approvals, reports
- **Staff** — Data entry, beneficiary management, assistance requests
- **Public** — Landing page, donor registration
- **Email/SMS Service** — Outbound notifications (Africa's Talking, SMTP)

---

## DFD Level 1 — Major Processes

```
DONOR ──[signup/login]──► [P1: User Auth] ──► DS1: Users DB
                                │
                          role token
                                │
DONOR ──[donation data]──► [P2: Donation Mgmt] ──► DS2: Donations DB
                                │                        │
                          receipt trigger         allocation data
                                │                        │
                          [P5: Notifications] ◄──── [P3: Fund Allocation]
                                │                        │
                         email/SMS queue          DS3: Allocations DB
                                │
STAFF ──[beneficiary data]──► [P4: Beneficiary Mgmt] ──► DS4: Beneficiaries DB
                                │
                          request data
                                │
ADMIN ──[approval action]──► [P6: Request Approval] ──► DS5: Requests DB
                                │
                          dashboard queries
                                │
ADMIN ──────────────────► [P7: Reporting Dashboard] ◄── DS1..DS5
                                │
                          PDF export
                                │
                          [P8: PDF Generator]
```

---

## DFD Level 2 — Donation Flow (Detailed)

```
DONOR fills form
      │
      ▼
[Validate donation form]
      │
      ├── invalid ──► Return error to DONOR
      │
      ▼
[Save Donation record] ──► donations_donation table
      │
      ├──► [Generate receipt number] ──► REC-YYYY-NNNNN
      │
      ├──► [Create DonationReceipt record]
      │
      ├──► [Queue Celery task: send_receipt_email]
      │              │
      │              ▼
      │       [Generate PDF via WeasyPrint]
      │              │
      │              ▼
      │       [Send SMTP email with PDF attachment]
      │              │
      │              ▼
      │       [Update EmailLog status: sent/failed]
      │
      ├──► [Create Notification for ADMIN: new_donation]
      │
      └──► [Check available_funds < LOW_FUNDS_THRESHOLD]
                     │
                     ├── YES ──► [Queue low_funds_alert to ADMIN]
                     └── NO ──► (end)
```

---

## DFD Level 2 — Assistance Request Flow

```
STAFF submits AssistanceRequest form
      │
      ▼
[Create AssistanceRequest] ──► status=PENDING
      │
      ├──► [Create Notification for ADMIN: pending_request]
      │
      ▼
ADMIN views pending requests on dashboard
      │
      ├── APPROVE ──► [Update status=APPROVED]
      │                     │
      │                     ├──► [Create Notification for STAFF: request_approved]
      │                     │
      │                     └──► [Allow DonationAllocation against this request]
      │
      └── REJECT ──► [Update status=REJECTED, add review_notes]
                           │
                           └──► [Create Notification for STAFF: request_rejected]
```

---

## DFD Level 2 — Donor-Beneficiary Update Flow

```
STAFF creates BeneficiaryUpdate (photo + progress text)
      │
      ▼
[Save BeneficiaryUpdate]
      │
      ▼
[Fetch all DonorBeneficiaryLink WHERE beneficiary=X AND is_active=TRUE]
      │
      ▼
FOR EACH linked donor:
      │
      ├──► [Queue Celery task: send_beneficiary_update_email(donor, beneficiary, update)]
      │
      └──► [Create in-app Notification for donor]
      │
      ▼
[Mark BeneficiaryUpdate.notified_donors = TRUE]
```

---

## Data Flow: Authentication & RBAC

```
User submits login credentials
      │
      ▼
[Django authenticate()] ──► Compare hashed password
      │
      ├── fail ──► Increment login_attempts, return error
      │
      ▼
[Get UserProfile.role]
      │
      ├── role=admin ──► Redirect /admin/dashboard/
      ├── role=staff ──► Redirect /staff/dashboard/
      └── role=donor ──► Redirect /donor/dashboard/

On every protected view:
      │
      ▼
[@login_required + @role_required('admin','staff')]
      │
      ├── authorized ──► Render view
      └── unauthorized ──► 403 Forbidden page
```

---

## State Diagrams

### Donation Status States
```
[received] ──(allocate all)──► [allocated]
[received] ──(allocate partial)──► [partial]
[partial]  ──(allocate rest)──► [allocated]
```

### Assistance Request States
```
[pending] ──(admin approve)──► [approved]
[pending] ──(admin reject)──► [rejected]
[approved] ──(funds allocated)──► [fulfilled]
```

### Beneficiary Status States
```
[active] ──(admin deactivate)──► [inactive]
[active] ──(aged out/completed)──► [graduated]
[inactive] ──(re-enrolled)──► [active]
```
