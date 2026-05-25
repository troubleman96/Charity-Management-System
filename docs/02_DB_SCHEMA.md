# Database Schema
## Charity Management System — PostgreSQL
---

## Entity Relationship Overview

```
User ──< Donor (1:1)
User ──< Staff (1:1)
Donor ──< Donation (1:many)
Donor ──< DonorBeneficiaryLink (1:many)
Beneficiary ──< DonorBeneficiaryLink (1:many)
Donation ──< DonationReceipt (1:1)
Donation ──< DonationAllocation (1:many)
Beneficiary ──< AssistanceRequest (1:many)
Beneficiary ──< BeneficiaryUpdate (1:many)
AssistanceRequest ──< DonationAllocation (1:many)
User ──< Message (sender, 1:many)
User ──< Message (recipient, 1:many)
User ──< Notification (1:many)
User ──< AuditLog (1:many)
```

---

## Table Definitions

### Table: `auth_user` (Django built-in, extended)

| Column | Type | Constraints | Notes |
|--------|------|-------------|-------|
| id | BIGINT | PK, AUTO | Django default |
| username | VARCHAR(150) | UNIQUE, NOT NULL | Email used as username |
| email | VARCHAR(254) | UNIQUE, NOT NULL | Primary login identifier |
| password | VARCHAR(128) | NOT NULL | PBKDF2/Argon2 hashed |
| first_name | VARCHAR(150) | | |
| last_name | VARCHAR(150) | | |
| is_active | BOOLEAN | DEFAULT TRUE | |
| is_staff | BOOLEAN | DEFAULT FALSE | Django admin access |
| date_joined | TIMESTAMP | AUTO | |

---

### Table: `accounts_userprofile`

Extends `auth_user` with system-specific fields.

| Column | Type | Constraints | Notes |
|--------|------|-------------|-------|
| id | BIGINT | PK, AUTO | |
| user_id | BIGINT | FK(auth_user), UNIQUE | OneToOne |
| role | VARCHAR(20) | NOT NULL | CHOICES: admin, staff, donor |
| phone | VARCHAR(20) | | |
| avatar | VARCHAR(255) | NULLABLE | File path |
| created_at | TIMESTAMP | AUTO_NOW_ADD | |
| updated_at | TIMESTAMP | AUTO_NOW | |

**Indexes:** `user_id`, `role`

---

### Table: `donors_donor`

| Column | Type | Constraints | Notes |
|--------|------|-------------|-------|
| id | BIGINT | PK, AUTO | |
| user_id | BIGINT | FK(auth_user), UNIQUE | |
| organization | VARCHAR(200) | NULLABLE | Org name if corporate donor |
| address | TEXT | NULLABLE | |
| national_id | VARCHAR(50) | NULLABLE | |
| is_anonymous | BOOLEAN | DEFAULT FALSE | |
| notes | TEXT | NULLABLE | Admin notes |
| created_at | TIMESTAMP | AUTO_NOW_ADD | |

**Indexes:** `user_id`

---

### Table: `beneficiaries_beneficiary`

| Column | Type | Constraints | Notes |
|--------|------|-------------|-------|
| id | BIGINT | PK, AUTO | |
| beneficiary_code | VARCHAR(20) | UNIQUE, NOT NULL | Auto-generated: BEN-2025-0001 |
| first_name | VARCHAR(100) | NOT NULL | |
| last_name | VARCHAR(100) | NOT NULL | |
| date_of_birth | DATE | NOT NULL | |
| gender | VARCHAR(10) | NOT NULL | CHOICES: male, female |
| photo | VARCHAR(255) | NULLABLE | File path |
| school_name | VARCHAR(200) | NULLABLE | |
| school_grade | VARCHAR(50) | NULLABLE | |
| health_status | TEXT | NULLABLE | |
| guardian_name | VARCHAR(200) | NULLABLE | |
| guardian_phone | VARCHAR(20) | NULLABLE | |
| guardian_relationship | VARCHAR(50) | NULLABLE | |
| location_region | VARCHAR(100) | NULLABLE | |
| location_district | VARCHAR(100) | NULLABLE | |
| date_enrolled | DATE | NOT NULL | |
| status | VARCHAR(20) | DEFAULT 'active' | CHOICES: active, inactive, graduated |
| notes | TEXT | NULLABLE | |
| registered_by_id | BIGINT | FK(auth_user) | |
| created_at | TIMESTAMP | AUTO_NOW_ADD | |
| updated_at | TIMESTAMP | AUTO_NOW | |

**Indexes:** `beneficiary_code`, `status`, `location_region`

---

### Table: `beneficiaries_donorllink`

Links donors to the specific beneficiaries they sponsor.

| Column | Type | Constraints | Notes |
|--------|------|-------------|-------|
| id | BIGINT | PK, AUTO | |
| donor_id | BIGINT | FK(donors_donor) | |
| beneficiary_id | BIGINT | FK(beneficiaries_beneficiary) | |
| start_date | DATE | NOT NULL | |
| end_date | DATE | NULLABLE | NULL = currently active |
| is_active | BOOLEAN | DEFAULT TRUE | |
| notes | TEXT | NULLABLE | |

**Constraints:** UNIQUE(donor_id, beneficiary_id)
**Indexes:** `donor_id`, `beneficiary_id`

---

### Table: `donations_donation`

| Column | Type | Constraints | Notes |
|--------|------|-------------|-------|
| id | BIGINT | PK, AUTO | |
| donation_ref | VARCHAR(30) | UNIQUE, NOT NULL | Auto: DON-2025-00001 |
| donor_id | BIGINT | FK(donors_donor), NULLABLE | NULL = anonymous |
| donation_type | VARCHAR(20) | NOT NULL | CHOICES: cash, in_kind |
| amount | DECIMAL(12,2) | NULLABLE | NULL if in_kind |
| in_kind_description | TEXT | NULLABLE | For in-kind donations |
| in_kind_estimated_value | DECIMAL(12,2) | NULLABLE | |
| donation_date | DATE | NOT NULL | |
| purpose | VARCHAR(200) | NULLABLE | e.g. "Education Fund" |
| status | VARCHAR(20) | DEFAULT 'received' | CHOICES: received, allocated, partial |
| payment_method | VARCHAR(30) | NULLABLE | CHOICES: cash, mpesa, tigopesa, bank, other |
| transaction_reference | VARCHAR(100) | NULLABLE | Mobile money ref |
| notes | TEXT | NULLABLE | |
| recorded_by_id | BIGINT | FK(auth_user) | Staff who recorded it |
| created_at | TIMESTAMP | AUTO_NOW_ADD | |
| updated_at | TIMESTAMP | AUTO_NOW | |

**Indexes:** `donation_ref`, `donor_id`, `donation_date`, `status`, `donation_type`

---

### Table: `donations_donationreceipt`

| Column | Type | Constraints | Notes |
|--------|------|-------------|-------|
| id | BIGINT | PK, AUTO | |
| donation_id | BIGINT | FK(donations_donation), UNIQUE | |
| receipt_number | VARCHAR(30) | UNIQUE, NOT NULL | REC-2025-00001 |
| pdf_file | VARCHAR(255) | NULLABLE | Generated PDF path |
| emailed_at | TIMESTAMP | NULLABLE | When email was sent |
| email_status | VARCHAR(20) | DEFAULT 'pending' | CHOICES: pending, sent, failed |
| created_at | TIMESTAMP | AUTO_NOW_ADD | |

---

### Table: `donations_donationallocation`

Tracks how donation funds are allocated to beneficiaries or programs.

| Column | Type | Constraints | Notes |
|--------|------|-------------|-------|
| id | BIGINT | PK, AUTO | |
| donation_id | BIGINT | FK(donations_donation) | |
| beneficiary_id | BIGINT | FK(beneficiaries_beneficiary), NULLABLE | |
| assistance_request_id | BIGINT | FK(beneficiaries_assistancerequest), NULLABLE | |
| amount | DECIMAL(12,2) | NOT NULL | |
| allocation_type | VARCHAR(50) | | CHOICES: education, food, medical, clothing, general |
| description | TEXT | NULLABLE | |
| allocated_by_id | BIGINT | FK(auth_user) | |
| allocated_at | TIMESTAMP | AUTO_NOW_ADD | |

---

### Table: `beneficiaries_assistancerequest`

| Column | Type | Constraints | Notes |
|--------|------|-------------|-------|
| id | BIGINT | PK, AUTO | |
| request_ref | VARCHAR(30) | UNIQUE | REQ-2025-0001 |
| beneficiary_id | BIGINT | FK(beneficiaries_beneficiary) | |
| requested_by_id | BIGINT | FK(auth_user) | Staff submitting |
| request_type | VARCHAR(50) | NOT NULL | CHOICES: education, food, medical, clothing, other |
| description | TEXT | NOT NULL | |
| estimated_cost | DECIMAL(12,2) | NULLABLE | |
| status | VARCHAR(20) | DEFAULT 'pending' | CHOICES: pending, approved, rejected, fulfilled |
| reviewed_by_id | BIGINT | FK(auth_user), NULLABLE | Admin who reviewed |
| review_notes | TEXT | NULLABLE | |
| created_at | TIMESTAMP | AUTO_NOW_ADD | |
| updated_at | TIMESTAMP | AUTO_NOW | |

**Indexes:** `beneficiary_id`, `status`, `request_type`

---

### Table: `beneficiaries_beneficiaryupdate`

Progress updates sent to linked donors.

| Column | Type | Constraints | Notes |
|--------|------|-------------|-------|
| id | BIGINT | PK, AUTO | |
| beneficiary_id | BIGINT | FK(beneficiaries_beneficiary) | |
| title | VARCHAR(200) | NOT NULL | |
| content | TEXT | NOT NULL | |
| photo | VARCHAR(255) | NULLABLE | |
| created_by_id | BIGINT | FK(auth_user) | |
| created_at | TIMESTAMP | AUTO_NOW_ADD | |
| notified_donors | BOOLEAN | DEFAULT FALSE | Whether donors were notified |

---

### Table: `communications_message`

Internal staff messaging.

| Column | Type | Constraints | Notes |
|--------|------|-------------|-------|
| id | BIGINT | PK, AUTO | |
| sender_id | BIGINT | FK(auth_user) | |
| recipient_id | BIGINT | FK(auth_user) | |
| subject | VARCHAR(255) | NOT NULL | |
| body | TEXT | NOT NULL | |
| is_read | BOOLEAN | DEFAULT FALSE | |
| read_at | TIMESTAMP | NULLABLE | |
| created_at | TIMESTAMP | AUTO_NOW_ADD | |

**Indexes:** `sender_id`, `recipient_id`, `is_read`

---

### Table: `communications_notification`

System notifications for all users.

| Column | Type | Constraints | Notes |
|--------|------|-------------|-------|
| id | BIGINT | PK, AUTO | |
| user_id | BIGINT | FK(auth_user) | |
| notification_type | VARCHAR(50) | | CHOICES: donation_received, low_funds, request_approved, request_rejected, update_available, system |
| title | VARCHAR(255) | NOT NULL | |
| message | TEXT | NOT NULL | |
| is_read | BOOLEAN | DEFAULT FALSE | |
| link | VARCHAR(500) | NULLABLE | URL to relevant page |
| created_at | TIMESTAMP | AUTO_NOW_ADD | |

**Indexes:** `user_id`, `is_read`, `created_at`

---

### Table: `communications_emaillog`

| Column | Type | Constraints | Notes |
|--------|------|-------------|-------|
| id | BIGINT | PK, AUTO | |
| recipient_email | VARCHAR(254) | NOT NULL | |
| subject | VARCHAR(255) | NOT NULL | |
| email_type | VARCHAR(50) | | CHOICES: donation_receipt, low_funds_alert, broadcast, update, password_reset |
| status | VARCHAR(20) | DEFAULT 'pending' | CHOICES: pending, sent, failed |
| celery_task_id | VARCHAR(255) | NULLABLE | |
| sent_at | TIMESTAMP | NULLABLE | |
| error_message | TEXT | NULLABLE | |
| created_at | TIMESTAMP | AUTO_NOW_ADD | |

---

### Table: `core_auditlog`

Immutable audit trail for security and accountability.

| Column | Type | Constraints | Notes |
|--------|------|-------------|-------|
| id | BIGINT | PK, AUTO | |
| user_id | BIGINT | FK(auth_user), NULLABLE | NULL = system action |
| action | VARCHAR(100) | NOT NULL | e.g. "donation.created", "request.approved" |
| object_type | VARCHAR(100) | NULLABLE | e.g. "Donation" |
| object_id | BIGINT | NULLABLE | PK of affected object |
| description | TEXT | NULLABLE | Human-readable summary |
| ip_address | VARCHAR(45) | NULLABLE | IPv4/IPv6 |
| user_agent | TEXT | NULLABLE | |
| timestamp | TIMESTAMP | AUTO_NOW_ADD | |

**Indexes:** `user_id`, `action`, `object_type`, `timestamp`

---

## Key Database Constraints

```sql
-- Prevent negative donation amounts
ALTER TABLE donations_donation ADD CONSTRAINT chk_amount_positive CHECK (amount >= 0);

-- Prevent negative allocations
ALTER TABLE donations_donationallocation ADD CONSTRAINT chk_alloc_positive CHECK (amount > 0);

-- Ensure donation type consistency
ALTER TABLE donations_donation ADD CONSTRAINT chk_inkind_has_desc 
    CHECK (donation_type != 'in_kind' OR in_kind_description IS NOT NULL);
```

---

## Computed Views (for Dashboard Performance)

```sql
-- Monthly donation summary view
CREATE VIEW v_monthly_donations AS
SELECT 
    DATE_TRUNC('month', donation_date) AS month,
    COUNT(*) AS donation_count,
    SUM(CASE WHEN donation_type='cash' THEN amount ELSE 0 END) AS cash_total,
    SUM(CASE WHEN donation_type='in_kind' THEN in_kind_estimated_value ELSE 0 END) AS inkind_total
FROM donations_donation
GROUP BY DATE_TRUNC('month', donation_date);

-- Available funds view
CREATE VIEW v_available_funds AS
SELECT 
    (SELECT COALESCE(SUM(amount),0) FROM donations_donation WHERE donation_type='cash') -
    (SELECT COALESCE(SUM(amount),0) FROM donations_donationallocation) AS available_balance;
```
