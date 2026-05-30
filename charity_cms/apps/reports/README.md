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
  - Generates a PDF directory, sorted by total contributions descending.

## URLs

```
/reports/          → Report index page (available downloads)
/reports/monthly/  → Generate monthly summary PDF
/reports/donors/   → Generate donor list PDF
```

## Templates

| Template | Status | Description |
|----------|--------|-------------|
| `reports/report_list.html` | ✅ Complete | Landing page with report download buttons |
| `reports/pdf/monthly_summary.html` | ✅ Complete | Monthly PDF: KPIs + donation transaction table |
| `reports/pdf/donor_report.html` | ✅ Complete | Donor PDF: ranked contribution table with highlights |

## Implementation Status

| Component | Status |
|-----------|--------|
| ReportIndexView | ✅ Complete |
| MonthlySummaryReportView | ✅ Complete |
| DonorReportView | ✅ Complete |
| PDF utility (`generate_pdf_response`) | ✅ Complete |
| Monthly summary PDF template | ✅ Complete |
| Donor report PDF template | ✅ Complete |
| Django admin | ✅ Complete |

## Notes

- Reports are generated **synchronously** (unlike donation receipts which use Celery).  
- WeasyPrint must be installed with system dependencies (`libpango`, `libcairo`) for PDF rendering to work.  
- All report views log an `AuditLog` entry on generation.
