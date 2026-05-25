# Reports App

The `reports` application is responsible for generating analytical data and exporting it to PDF formats for offline review by administrators or board members.

## Concept
Reporting views aggregate data across multiple apps (donations, beneficiaries) and use `WeasyPrint` to generate downloadable documents. Unlike the `donations` app where PDFs are generated asynchronously by Celery and emailed, `reports` generates PDFs synchronously in the web request so the user can download them immediately.

## Key Views (`views.py`)
*All views are protected by `AdminRequiredMixin`.*

- **`MonthlySummaryPDFView`**: 
  - Aggregates the total donations received in the current month.
  - Aggregates total funds allocated in the current month.
  - Counts newly enrolled beneficiaries.
  - Renders a professional HTML template and converts it to PDF via HTTP Response.

- **`DonorDirectoryPDFView`**:
  - Compiles a list of all donors, their contact info (from `UserProfile`), and their lifetime contribution totals.
  - Generates a PDF directory.
