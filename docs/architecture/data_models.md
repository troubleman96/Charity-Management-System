# Data Models & Schema

CharityOS utilizes a relational PostgreSQL (or SQLite for dev) database. The schema is highly normalized to ensure data integrity, especially concerning financial transactions (donations) and human entities (beneficiaries/donors).

## Core Entity Relationships

### 1. User & Accounts (`apps.accounts`)
Django's default `User` model handles authentication (username, password, email). We extend this using a `OneToOneField` in the `UserProfile` model.
- **`UserProfile`**: Stores the `role` (`admin`, `staff`, `donor`), phone number, and a profile picture.
- **Signal**: `post_save` on `User` automatically creates a `UserProfile`.

### 2. Donors (`apps.donors`)
If a `UserProfile` has the role `donor`, a corresponding `Donor` record is created (or linked).
- **`Donor`**: Links 1:1 to `UserProfile`. Contains donor-specific fields like `organization_name`, `is_anonymous` preference, and helper methods to aggregate their total lifetime donations (`get_total_donated()`).

### 3. Beneficiaries (`apps.beneficiaries`)
The core subject of the system.
- **`Beneficiary`**: Represents an orphan. Tracks PII, demographics, education status, and a unique `beneficiary_code`.
- **`AssistanceRequest`**: A Many-to-One relationship to `Beneficiary`. Represents a specific need (e.g., Medical Bill, School Fees). It has an `estimated_cost` and a `status` (`pending`, `approved`, `funded`).
- **`ProgressUpdate`**: A Many-to-One relationship to `Beneficiary`. A journal entry logging the child's progress (e.g., term grades).
- **`DonorBeneficiaryLink`**: A Many-to-Many through table connecting `Donor` and `Beneficiary`. Allows a donor to sponsor specific children and limits their portal view to only those children.

### 4. Financial Tracking (`apps.donations`)
Handles all incoming resources.
- **`Donation`**: Represents a physical receipt of resources. It has a `donation_type` (`cash` or `in_kind`).
    - If `cash`, it has an `amount` and `available_balance`.
    - It tracks its state via `status` (`unallocated`, `partially_allocated`, `fully_allocated`).
- **`DonationAllocation`**: Maps exactly *where* a `Donation`'s cash was spent. It links a `Donation` to an `AssistanceRequest`. When created, it deducts its `amount` from the parent `Donation.available_balance`.
- **`DonationReceipt`**: A record of the PDF receipt generated and sent to the donor, linking to the `Donation`.

### 5. System Tracking
- **`AuditLog` (`apps.core`)**: A generic tracking table. It uses `GenericForeignKey` to attach an audit event to *any* model in the system. It records the `User` who made the change, the `action` (`CREATE`, `UPDATE`, `DELETE`), and the `ip_address`.
- **`Message` (`apps.communications`)**: Internal staff-to-staff messaging. Links a `sender` (User) and `recipient` (User).

## ERD Diagram Summary
```text
User (Django Auth)
  │
  ├─ 1:1 ─ UserProfile (Role, Phone)
  │
  └─ 1:1 (If Donor) ─ Donor (Organization, Preferences)
                        │
                        ├─ 1:N ─ Donation (Cash/In-Kind) ─ 1:N ─ DonationAllocation
                        │                                             │
                        └─ M:N ─ DonorBeneficiaryLink                 │
                                      │                               │
                                      └─ M:1 ─ Beneficiary ─ 1:N ─ AssistanceRequest
                                                    │
                                                    └─ 1:N ─ ProgressUpdate
```
