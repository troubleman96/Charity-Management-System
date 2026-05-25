"""
CharityOS — Reports Utilities
================================
Helpers for PDF generation using WeasyPrint.
"""
import weasyprint
from django.template.loader import render_to_string
from django.conf import settings
from django.http import HttpResponse


def generate_pdf_response(template_name, context, filename):
    """
    Renders a Django template to HTML, converts it to PDF via WeasyPrint,
    and returns a Django HttpResponse for the user to download.

    Args:
        template_name: Path to the HTML template
        context: Context dict for the template
        filename: Name of the generated PDF file (e.g., 'report.pdf')
    """
    html_string = render_to_string(template_name, context)
    pdf_file = weasyprint.HTML(string=html_string, base_url=settings.BASE_DIR).write_pdf()

    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response
