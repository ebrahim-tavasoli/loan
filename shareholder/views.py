from django.shortcuts import render, get_object_or_404
from django.template.loader import render_to_string
from .models import Shareholder
from loan.logics import return_pdf

def shareholder_contract(request, shareholder_id):
    shareholder = get_object_or_404(Shareholder, id=shareholder_id)
    context = {
        "shares": shareholder.total_shares,
        "amount": shareholder.total_shares * 1000,
    }
    html_content = render_to_string("admin/shareholder/shareholder_contract.html", context)
    return return_pdf(html_content, "report.pdf")
