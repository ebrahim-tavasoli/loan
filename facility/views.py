from django.shortcuts import render, get_object_or_404
from django.template.loader import render_to_string
import jdatetime
from .models import Facility, FacilitySetting, FacilityRequest, FacilityType
from loan.logics import return_pdf

from num2fawords import words
from django.http import HttpResponse
from weasyprint import HTML
import os
from shareholder.models import Shareholder
from django.db.models import Q


def generate_contract_view(request, facility_id):
    """Render contract template with facility data and generate PDF"""
    facility = get_object_or_404(Facility, pk=facility_id)
    shareholder = facility.facility_request.shareholder

    # Fetch financial instruments (checks & promissory notes)
    checks = facility.facility_check.all()
    promissory_notes = facility.facility_promissory_note.all()

    # Fetch all guarantors related to this facility
    guarantors = facility.guarantors.all()

    context = {
        "facility": facility,
        "shareholder": shareholder,
        "contract_number": facility.id,
        "contract_date": facility.start_date if facility.start_date else "...",
        "amount_in_words": (
            str(facility.amount) if facility.amount else "..."
        ),
        "loan_amount": facility.amount,
        "loan_amount_words": words(facility.amount),
        "due_date": facility.end_date if facility.end_date else "...",
        "duration_months": (
            ((facility.end_date - facility.start_date).days // 30)
            if facility.start_date and facility.end_date
            else "..."
        ),
        "additional_amount": facility.profit if facility.profit else "...",
        # Borrower Details
        "borrower_name": shareholder.name,
        "borrower_father_name": (
            shareholder.father_name if shareholder.father_name else "..."
        ),
        "borrower_id_number": shareholder.id_number if shareholder.id_number else "...",
        "borrower_national_id": (
            shareholder.melli_code if shareholder.melli_code else "..."
        ),
        "borrower_city": shareholder.city if shareholder.city else "...",
        "borrower_phone": shareholder.phone if shareholder.phone else "...",
        # Check Details
        "check_count": checks.count(),
        "checks": checks,
        # Promissory Note
        "promissories_count": len(promissory_notes),
        "promissories": promissory_notes,
        # Guarantor List
        "guarantors": guarantors,
        # Additional Facility Details
        "purchase_item": facility.purchase_item if facility.purchase_item else "...",
        "for_target": facility.for_target if facility.for_target else "...",
        "power_of_attorney_number": (
            facility.power_of_attorney_number
            if facility.power_of_attorney_number
            else "..."
        ),
        "power_of_attorney_date": (
            facility.power_of_attorney_date
            if facility.power_of_attorney_date
            else "..."
        ),
        "start_date": facility.start_date if facility.start_date else "...",
        "end_date": facility.end_date if facility.end_date else "...",
        "facility_days": facility.facility_days,
        "facility_type": facility.facility_request.facility_type if facility.facility_request.facility_type else "...",
        "delay_repayment_penalty": (
            facility.delay_repayment_penalty
            if facility.delay_repayment_penalty
            else "..."
        ),
    }

    html_string = render_to_string("admin/facility/contract_template.html", context)

    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    static_root = os.path.join(base_dir, "staticfiles")

    html_string = (
        html_string.replace(
            "/static/facility/img/tashilat1.jpg",
            f"file://{static_root}/facility/img/tashilat1.jpg",
        )
        .replace(
            "/static/facility/font/nazanin-400.woff2",
            f"file://{static_root}/facility/font/nazanin-400.woff2",
        )
        .replace(
            "/static/facility/font/nazanin-700.woff2",
            f"file://{static_root}/facility/font/nazanin-700.woff2",
        )
    )

    pdf_file = HTML(string=html_string, base_url=static_root).write_pdf()

    filename = context.get("contract_number")
    response = HttpResponse(pdf_file, content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="contract_{filename}.pdf"'
    return response


def generate_form4_view(request, facility_request_id):
    """Render Form 4 template for a specific Facility and generate PDF"""
    facility = get_object_or_404(Facility, pk=facility_request_id)
    shareholder = facility.facility_request.shareholder

    guarantors = facility.guarantors.all()
    checks = facility.facility_check.all()
    promissory_note = facility.facility_promissory_note.all()
    

    context = {
        "facility": facility,
        "county_name": shareholder.city,
        "borrower_name": shareholder.name,
        "amount_requested": facility.facility_request.amount if facility.facility_request.amount else "...",
        "amount_received": (
            facility.amount if facility.amount else "..."
        ),
        "duration_months": (
            (round((facility.end_date - facility.start_date).days / 30))
            if facility.start_date and facility.end_date
            else "..."
        ),
        "interest_rate": facility.interest_rate if facility.interest_rate else "...",
        "investment_type": facility.facility_request.facility_type.name,
        "description": facility.description if facility.description else "...",
        "checks_count": checks.count(),
        "promissory_note_count": promissory_note.count(),
        "guarantors": guarantors,
    }

    # رندر HTML به صورت رشته
    html_string = render_to_string("admin/facility/form4_template.html", context)

    # مسیر پایه پروژه و پوشه staticfiles
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    static_root = os.path.join(base_dir, "staticfiles")

    # چک کردن مسیرها برای دیباگ
    nazanin_400_path = os.path.join(
        static_root, "facility", "font", "nazanin-400.woff2"
    )
    nazanin_700_path = os.path.join(
        static_root, "facility", "font", "nazanin-700.woff2"
    )
    html_string = html_string.replace(
        "/static/facility/font/nazanin-400.woff2", f"file://{nazanin_400_path}"
    ).replace("/static/facility/font/nazanin-700.woff2", f"file://{nazanin_700_path}")


    pdf_file = HTML(string=html_string, base_url=static_root).write_pdf()

    filename = context.get("facility").id
    response = HttpResponse(pdf_file, content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="form4_{filename}.pdf"'
    return response


def generate_financial_report(request, year=None):
    today_jalali = jdatetime.date.today()
    year = year if year is not None else today_jalali.year

    fiscal_start = FacilitySetting.current_fiscal_year_start_date()
    if year != today_jalali.year:
        fiscal_start = jdatetime.date(year, fiscal_start.month, fiscal_start.day)

    fiscal_end_year = fiscal_start.year + 1
    fiscal_end_month = fiscal_start.month
    fiscal_end_day = fiscal_start.day
    days_in_end_month = (
        31
        if fiscal_end_month <= 6
        else (
            30
            if fiscal_end_month <= 11
            else (30 if jdatetime.date(fiscal_end_year, 12, 1).isleap() else 29)
        )
    )
    fiscal_end = jdatetime.date(
        fiscal_end_year, fiscal_end_month, min(fiscal_end_day, days_in_end_month)
    ) - jdatetime.timedelta(days=1)

    month_names = [
        "فروردین",
        "اردیبهشت",
        "خرداد",
        "تیر",
        "مرداد",
        "شهریور",
        "مهر",
        "آبان",
        "آذر",
        "دی",
        "بهمن",
        "اسفند",
    ]

    all_facilities = Facility.objects.filter(
        start_date__lte=fiscal_end, end_date__gte=fiscal_start
    )
    total_unique_cases = all_facilities.count()

    rows = []
    total_loans = 0
    total_definite_income = 0
    total_transferred_income = 0
    total_insurance = 0
    total_tax = 0
    total_net_payments = 0
    total_repayments = 0

    for i in range(12):
        month_offset = (fiscal_start.month - 1 + i) % 12
        month = month_offset + 1
        year_adj = fiscal_start.year + ((fiscal_start.month - 1 + i) // 12)

        start_date = jdatetime.date(year_adj, month, 1)
        days_in_month = (
            31
            if month <= 6
            else (
                30
                if month <= 11
                else (30 if jdatetime.date(year_adj, 12, 1).isleap() else 29)
            )
        )
        end_date = jdatetime.date(year_adj, month, days_in_month)
        if end_date > fiscal_end:
            end_date = fiscal_end

        facilities_starting = all_facilities.filter(
            start_date__gte=start_date, start_date__lte=end_date
        )
        num_cases = facilities_starting.count()

        month_loans = 0
        month_definite_income = 0
        month_transferred_income = 0
        month_insurance = 0
        month_tax = 0
        month_net_payments = 0

        for facility in all_facilities:
            if facility.start_date <= end_date and facility.end_date >= start_date:
                period_start = max(facility.start_date, start_date)
                period_end = min(facility.end_date, end_date)
                days_in_month_for_facility = (period_end - period_start).days + 1
                total_days = (facility.end_date - facility.start_date).days + 1

                month_loans += (
                    (facility.amount or 0)
                    * days_in_month_for_facility
                    // total_days
                )
                month_definite_income += (
                    (facility.definite_income or 0)
                    * days_in_month_for_facility
                    // total_days
                )
                month_transferred_income += (
                    (facility.transferred_income or 0)
                    * days_in_month_for_facility
                    // total_days
                )

                month_insurance += (
                    (facility.insurance_amount or 0)
                    * days_in_month_for_facility
                    // total_days
                )
                month_tax += (
                    (facility.tax_amount or 0)
                    * days_in_month_for_facility
                    // total_days
                )
                month_net_payments += (
                    (facility.total_payment or 0)
                    * days_in_month_for_facility
                    // total_days
                )

        rows.append(
            {
                "index": i + 1,
                "company_name": month_names[month_offset],
                "start_date": start_date.strftime("%Y/%m/%d"),
                "end_date": end_date.strftime("%Y/%m/%d"),
                "num_cases": num_cases,
                "amount_received": month_loans,
                "total_payment": month_net_payments,
                "added_value": month_tax,
                "insurance": month_insurance,
                "definite_income": month_definite_income,
                "transferred_income": month_transferred_income,
                "net_payment": month_net_payments - (month_tax + month_insurance),
            }
        )

        total_loans += month_loans
        total_definite_income += month_definite_income
        total_transferred_income += month_transferred_income
        total_insurance += month_insurance
        total_tax += month_tax
        total_net_payments += month_net_payments - (month_tax + month_insurance)
        total_repayments += month_net_payments

    context = {
        "year": year,
        "facilities": rows,
        "total_loans": total_loans,
        "total_definite_income": total_definite_income,
        "total_transferred_income": total_transferred_income,
        "total_insurance": total_insurance,
        "total_tax": total_tax,
        "total_net_payments": total_net_payments,
        "total_repayments": total_repayments,
        "total_cases": total_unique_cases,
    }

    html_string = render_to_string("admin/facility/financial_report.html", context)

    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    static_root = os.path.join(base_dir, "staticfiles")

    nazanin_400_path = os.path.join(
        static_root, "facility", "font", "nazanin-400.woff2"
    )
    nazanin_700_path = os.path.join(
        static_root, "facility", "font", "nazanin-700.woff2"
    )

    html_string = html_string.replace(
        "/static/facility/font/nazanin-400.woff2", f"file://{nazanin_400_path}"
    ).replace("/static/facility/font/nazanin-700.woff2", f"file://{nazanin_700_path}")

    pdf_file = HTML(string=html_string, base_url=static_root).write_pdf()

    response = HttpResponse(pdf_file, content_type="application/pdf")
    response["Content-Disposition"] = (
        f'attachment; filename="financial_report_{year}.pdf"'
    )
    return response


def generate_facility_report_by_filter(request):
    """Generate a PDF report of facilities with filtering options"""
    from django.template.loader import render_to_string
    from weasyprint import HTML
    from django.http import HttpResponse
    import os
    import jdatetime

    # Get filter parameters from request
    facility_type = request.GET.get('facility_type')
    from_date = request.GET.get('from_date')
    to_date = request.GET.get('to_date')
    
    # Base query for facilities
    facilities = Facility.objects.all()
    
    # Apply filters if provided
    if facility_type:
        facilities = facilities.filter(
            facility_request__facility_type__id=facility_type
        )
    
    if from_date:
        # Convert Jalali date string to jdatetime object
        try:
            from_date = jdatetime.datetime.strptime(from_date, '%Y-%m-%d').date()
            facilities = facilities.filter(start_date__gte=from_date)
        except ValueError:
            pass
    
    if to_date:
        # Convert Jalali date string to jdatetime object
        try:
            to_date = jdatetime.datetime.strptime(to_date, '%Y-%m-%d').date()
            facilities = facilities.filter(start_date__lte=to_date)
        except ValueError:
            pass

    
    html_string = render_to_string("admin/facility/facility_report_filter.html", {"facilities": facilities})

    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    static_root = os.path.join(base_dir, "staticfiles")

    nazanin_400_path = os.path.join(
        static_root, "facility", "font", "nazanin-400.woff2"
    )
    nazanin_700_path = os.path.join(
        static_root, "facility", "font", "nazanin-700.woff2"
    )

    html_string = html_string.replace(
        "/static/facility/font/nazanin-400.woff2", f"file://{nazanin_400_path}"
    ).replace("/static/facility/font/nazanin-700.woff2", f"file://{nazanin_700_path}")

    pdf_file = HTML(string=html_string, base_url=static_root).write_pdf()

    response = HttpResponse(pdf_file, content_type="application/pdf")
    response["Content-Disposition"] = (
        f'attachment; filename="facility_report_{facility_type}_{from_date}_{to_date}.pdf"'
    )
    return response

def request_facility(request, id):
    req = get_object_or_404(FacilityRequest, id=id)
    
    html_string = render_to_string("admin/facility/request_facility.html", {"facility_request": req})

    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    static_root = os.path.join(base_dir, "staticfiles")

    nazanin_400_path = os.path.join(
        static_root, "facility", "font", "nazanin-400.woff2"
    )
    nazanin_700_path = os.path.join(
        static_root, "facility", "font", "nazanin-700.woff2"
    )

    html_string = html_string.replace(
        "/static/facility/img/tashilat1.jpg",
        f"file://{static_root}/facility/img/tashilat1.jpg",
    ).replace(
        "/static/facility/font/nazanin-400.woff2", f"file://{nazanin_400_path}"
    ).replace("/static/facility/font/nazanin-700.woff2", f"file://{nazanin_700_path}")

    pdf_file = HTML(string=html_string, base_url=static_root).write_pdf()

    response = HttpResponse(pdf_file, content_type="application/pdf")
    response["Content-Disposition"] = (
        f'attachment; filename="request_facility_{req.shareholder.name}.pdf"'
    )
    return response
