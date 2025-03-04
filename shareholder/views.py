from django.shortcuts import render, get_object_or_404
from django.template.loader import render_to_string
from .models import Shareholder
from django.http import HttpResponse
from weasyprint import HTML
import os


def shareholder_contract(request, shareholder_id):
    """Generate share certificate PDF for a specific Shareholder"""
    shareholder = get_object_or_404(Shareholder, pk=shareholder_id)

    context = {
        "shares": shareholder.total_shares,
        "amount": shareholder.total_shares * 1000,
    }

    html_string = render_to_string(
        "admin/shareholder/shareholder_contract.html", context
    )

    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    static_root = os.path.join(base_dir, "staticfiles")

    nazanin_400_path = os.path.join(
        static_root, "shareholder", "font", "nazanin-400.woff2"
    )
    nazanin_700_path = os.path.join(
        static_root, "shareholder", "font", "nazanin-700.woff2"
    )

    html_string = html_string.replace(
        "/static/shareholder/font/nazanin-400.woff2", f"file://{nazanin_400_path}"
    ).replace(
        "/static/shareholder/font/nazanin-700.woff2", f"file://{nazanin_700_path}"
    )

    pdf_file = HTML(string=html_string, base_url=static_root).write_pdf()

    filename = shareholder.id
    response = HttpResponse(pdf_file, content_type="application/pdf")
    response["Content-Disposition"] = (
        f'attachment; filename="share_certificate_{filename}.pdf"'
    )
    return response
