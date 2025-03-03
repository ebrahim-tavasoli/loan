from django.shortcuts import render, get_object_or_404
from django.template.loader import render_to_string
import jdatetime
from .models import Facility, FacilitySetting
from loan.logics import return_pdf


def generate_contract_view(request, facility_id):
    """Render contract template with facility data"""
    facility = get_object_or_404(Facility, pk=facility_id)
    shareholder = facility.shareholder

    # Fetch financial instruments (checks & promissory notes)
    financial_instruments = facility.financial_instruments.all()
    checks = financial_instruments.filter(instrument_type="check")
    promissory_notes = financial_instruments.filter(instrument_type="promissory_note")

    # Fetch all guarantors related to this facility
    guarantors = facility.guarantors.all()

    context = {
        "facility": facility,
        "shareholder": shareholder,
        "contract_number": facility.id,
        "contract_date": facility.start_date if facility.start_date else "...",
        "amount_in_words": (
            str(facility.amount_received) if facility.amount_received else "..."
        ),
        "loan_amount": facility.amount_received,
        "loan_amount_words": ".............",
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
        "check_number": checks[0].number if checks else "...",
        "account_number": checks[0].account_number if checks else "...",
        "bank_name": checks[0].bank_name if checks else "...",
        "branch_name": checks[0].branch_name if checks else "...",
        "bank_code": checks[0].bank_code if checks else "...",
        "check_amount": checks[0].amount if checks else "...",
        "check_owner": checks[0].owner_name if checks else "...",
        # Promissory Notes
        "promissory_note_number": (
            promissory_notes[0].number if promissory_notes else "..."
        ),
        "promissory_note_amount": (
            promissory_notes[0].amount if promissory_notes else "..."
        ),
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
        "facility_type": facility.facility_type if facility.facility_type else "...",
        "delay_repayment_penalty": (
            facility.delay_repayment_penalty
            if facility.delay_repayment_penalty
            else "..."
        ),
    }

    html_content = render_to_string("admin/facility/contract_template.html", context)
    filename = context.get("contract_number")
    return return_pdf(html_content, f"{filename}")


def generate_form4_view(request, facility_id):
    """Render Form 4 template for a specific Facility"""
    facility = get_object_or_404(Facility, pk=facility_id)

    shareholder = facility.shareholder

    guarantors = facility.guarantors.all()
    financial_instruments = facility.financial_instruments.all()

    first_instrument = financial_instruments.first()

    context = {
        "facility": facility,
        "county_name": shareholder.city,
        "meeting_number": "...",  # TODO: What is this?
        "meeting_date": "...",  # TODO: What is this?
        "borrower_name": shareholder.name,
        "amount_requested": facility.amount if facility.amount else "...",
        "amount_received": (
            facility.amount_received if facility.amount_received else "..."
        ),
        "duration_months": (
            ((facility.end_date - facility.start_date).days // 30)
            if facility.start_date and facility.end_date
            else "..."
        ),
        "interest_rate": facility.interest_rate if facility.interest_rate else "...",
        "investment_type": facility.facility_type.fa_name,
        "description": facility.description if facility.description else "...",
        "financial_instruments": financial_instruments,
        "guarantors": guarantors,
        "receipt_number": first_instrument.number if first_instrument else "-",
        "receipt_date": "..........",
        "receipt_amount": first_instrument.amount if first_instrument else "-",
    }

    html_content = render_to_string("admin/facility/form4_template.html", context)
    filename = context.get("facility").id
    return return_pdf(html_content, f"{filename}")


def generate_financial_report(request, year=None):
    """Generate monthly financial report for a given Persian fiscal year (Unique Starts)"""

    today_jalali = jdatetime.date.today()
    year = year if year is not None else today_jalali.year

    # Get fiscal year start and end dates
    fiscal_start = FacilitySetting.current_fiscal_year_start_date()
    if year != today_jalali.year:
        fiscal_start = jdatetime.date(year, fiscal_start.month, fiscal_start.day)

    fiscal_end_year = fiscal_start.year + 1
    fiscal_end_month = fiscal_start.month
    fiscal_end_day = fiscal_start.day
    days_in_end_month = 31 if fiscal_end_month <= 6 else (
        30 if fiscal_end_month <= 11 else (30 if jdatetime.date(fiscal_end_year, 12, 1).isleap() else 29))
    fiscal_end = jdatetime.date(fiscal_end_year, fiscal_end_month,
                                min(fiscal_end_day, days_in_end_month)) - jdatetime.timedelta(days=1)

    # Define month names in Persian
    month_names = ['فروردین', 'اردیبهشت', 'خرداد', 'تیر', 'مرداد', 'شهریور', 'مهر', 'آبان', 'آذر', 'دی', 'بهمن',
                   'اسفند']

    # Fetch all facilities active in the fiscal year
    all_facilities = Facility.objects.filter(
        start_date__lte=fiscal_end,
        end_date__gte=fiscal_start
    )
    total_unique_cases = all_facilities.count()

    # Prepare monthly data
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
        days_in_month = 31 if month <= 6 else (
            30 if month <= 11 else (30 if jdatetime.date(year_adj, 12, 1).isleap() else 29))
        end_date = jdatetime.date(year_adj, month, days_in_month)
        if end_date > fiscal_end:
            end_date = fiscal_end

        # Count facilities starting in this month
        facilities_starting = all_facilities.filter(
            start_date__gte=start_date,
            start_date__lte=end_date
        )
        num_cases = facilities_starting.count()

        # Calculate prorated financial metrics for active facilities
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

                month_loans += (facility.amount_received or 0) * days_in_month_for_facility // total_days
                month_definite_income += (facility.definite_income or 0) * days_in_month_for_facility // total_days
                month_transferred_income += (
                                                        facility.transferred_income or 0) * days_in_month_for_facility // total_days
                month_insurance += (facility.insurance_amount or 0) * days_in_month_for_facility // total_days
                month_tax += (facility.tax_amount or 0) * days_in_month_for_facility // total_days
                month_net_payments += (facility.total_payment or 0) * days_in_month_for_facility // total_days

        rows.append({
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
        })

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

    html_content = render_to_string("admin/facility/financial_report.html", context)
    return return_pdf(html_content, "report")
