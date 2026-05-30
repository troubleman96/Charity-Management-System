# Donors App

The `donors` application provides the Donor Portal experience and manages donor-specific metadata.

## Concept
While `apps.accounts` handles the login credentials and profile of a user, the `donors` app handles the business logic associated with someone giving money to the NGO.

## Models
- **`Donor`**: Links 1:1 to a `UserProfile` (where `role == 'donor'`). Contains fields like `organization_name`, `is_anonymous` (preference for public recognition), and notes.
- **Aggregations**: The model includes helper properties like `get_total_donated()` which queries the `donations` app to sum all cash contributions for this specific donor.

## Views (`views.py`)
*Views are strictly protected by `DonorRequiredMixin`.*
- **`DonorDashboardView`**: The primary landing page for a donor. It fetches:
  1. KPI metrics (Total Donated, Number of Donations).
  2. The donor's recent `Donation` history.
  3. The specific `Beneficiary` records linked to them via `DonorBeneficiaryLink`.
  4. Recent `ProgressUpdate` entries for their sponsored children, creating a personalized feed of impact.

## URLs

```
/donor/dashboard/   → Donor dashboard (DonorDashboardView)
/donor/history/     → Full paginated donation history (DonationHistoryView)
```

## Templates

| Template | Status | Description |
|----------|--------|-------------|
| `donor_portal/dashboard.html` | ✅ Complete | KPIs, sponsored beneficiaries, recent updates |
| `donor_portal/donation_history.html` | ✅ Complete | Paginated donation history with receipt download links |

## Implementation Status

| Component | Status |
|-----------|--------|
| Donor model | ✅ Complete |
| Donor profile form | ✅ Complete |
| Donor dashboard view | ✅ Complete |
| Donation history view | ✅ Complete |
| All templates | ✅ Complete |
| Django admin | ✅ Complete |
