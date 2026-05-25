# Donations App

The `donations` application handles all incoming resources, financial tracking, allocation of funds to specific needs, and the generation of digital receipts.

## Key Concepts
CharityOS treats donations strictly. Once a donation is logged, it cannot be quietly deleted. It must be allocated, and any changes are tracked via the `AuditLog`.

## Models
- **`Donation`**: The core ledger entry. Tracks the `donor`, `donation_type` (cash or in-kind), date, and purpose. 
  - If it's a cash donation, it has an `amount` and an `available_balance`.
  - The `save()` method contains logic to automatically update the `status` based on how much of the balance has been allocated.
- **`DonationAllocation`**: Links a `Donation` to an `AssistanceRequest` (from the `beneficiaries` app). When saved, it reduces the `available_balance` of the parent `Donation` and increases the `amount_funded` on the `AssistanceRequest`.
- **`DonationReceipt`**: A record of a generated PDF receipt.

## Asynchronous Tasks (Celery)
Financial operations like generating PDFs or sending emails block the main thread. We use Celery in `tasks.py`.
- **`send_donation_receipt(donation_id)`**: Triggered automatically when a new donation is logged. It uses `WeasyPrint` to render an HTML template into a PDF, attaches it to an email, and sends it to the donor asynchronously.
- **`check_low_funds()`**: A scheduled task (Beat) that checks if the total unallocated cash balance in the system falls below a threshold, alerting admins if so.

## Views (`views.py`)
- **`DonationCreateView`**: Protected by `StaffRequiredMixin`. Uses JavaScript to dynamically toggle form fields based on whether the user selects "Cash" or "In-Kind". Upon successful save, it dispatches the Celery task for the receipt.
