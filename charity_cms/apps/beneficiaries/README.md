# Beneficiaries App

The `beneficiaries` application is the heart of CharityOS operations. It tracks the orphans enrolled in the NGO's program, their needs, their progress, and their sponsors.

## Key Components

### Models
- **`Beneficiary`**: The core record for a child. Automatically generates a unique `beneficiary_code` upon creation. Tracks demographics, school information, health status, and guardian details.
- **`AssistanceRequest`**: A specific financial or material need tied to a `Beneficiary` (e.g., "Term 2 School Fees"). It has an `estimated_cost` and moves through statuses (`pending`, `partially_funded`, `funded`, `fulfilled`).
- **`ProgressUpdate`**: A text log tied to a `Beneficiary`. Used by staff to record milestones (e.g., "Passed exams", "Recovered from malaria"). These updates are visible to linked Donors.
- **`DonorBeneficiaryLink`**: A mapping table. It allows a Donor to be officially linked as a sponsor to a Beneficiary.

### Views (`views.py`)
*All views are protected by `StaffRequiredMixin`.*
- **`BeneficiaryListView`**: A paginated list of all children, with search and filtering by status/region using Django forms.
- **`BeneficiaryDetailView`**: A comprehensive dashboard for a single child. It aggregates and displays their profile, active sponsors, assistance history, and progress updates on one page.
- **CRUD Views**: Standard `CreateView` and `UpdateView` implementations that integrate with `apps.core.utils.log_action` to record audit logs whenever a staff member edits a child's record.

## Data Flow Example: Logging a Need
1. Staff navigates to a Beneficiary profile.
2. Clicks "Add Request".
3. Fills out the `AssistanceRequestForm` (e.g., Medical Need, 50,000 TZS).
4. The view saves the request, linking it to the child, and writes an AuditLog.
5. The request is now visible in the child's profile and pending funding from the `donations` app.
