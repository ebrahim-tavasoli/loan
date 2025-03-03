from django.shortcuts import render, get_object_or_404
import jdatetime
from .models import Facility


def generate_contract_view(request, facility_id):
    """Render contract template with facility data"""
    facility = get_object_or_404(Facility, pk=facility_id)
    shareholder = facility.shareholder

    # Fetch all financial instruments
    checks = facility.financial_instruments.filter(instrument_type="check")
    promissory_notes = facility.financial_instruments.filter(
        instrument_type="promissory_note"
    )

    context = {
        "facility": facility,
        "shareholder": shareholder,
        "contract_number": facility.id,
        "contract_date": facility.start_date if facility.start_date else "...",
        "amount_in_words": (
            str(facility.amount_received) if facility.amount_received else "..."
        ),
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
        "borrower_city": shareholder.address if shareholder.address else "...",
        "borrower_phone": shareholder.phone if shareholder.phone else "...",
        # Check Details
        "check_count": len(checks),
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
    }

    return render(request, "admin/facility/contract_template.html", context)


def generate_form4_view(request, facility_id):
    """Render Form 4 template for a specific Facility"""
    facility = get_object_or_404(Facility, pk=facility_id)

    guarantors = facility.guarantors.all()
    financial_instruments = facility.financial_instruments.all()

    first_instrument = financial_instruments.first()

    context = {
        "facility": facility,
        "county_name": "نام شهرستان",
        "meeting_number": "...",
        "meeting_date": "...",
        # Loan Details
        "borrower_name": facility.shareholder.name,
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
        # Financial Instruments
        "financial_instruments": financial_instruments,
        # Guarantors
        "guarantors": guarantors,
        # Receipt
        "receipt_number": first_instrument.number if first_instrument else "-",
        "receipt_date": first_instrument.issued_by if first_instrument else "-",
        "receipt_amount": first_instrument.amount if first_instrument else "-",
    }

    return render(request, "admin/facility/form4_template.html", context)


def generate_financial_report(request, year=None):
    """Generate the financial report for a given Persian year"""

    today_jalali = jdatetime.date.today()
    start_of_year = jdatetime.date(today_jalali.year, 10, 1)  # 1 Dey
    end_of_year = jdatetime.date(today_jalali.year + 1, 2, 30)  # 30 Ordibehesht

    # Fetch facilities within the selected year range
    facilities = Facility.objects.filter(
        start_date__gte=start_of_year, end_date__lte=end_of_year
    )

    total_loans = sum(f.amount_received or 0 for f in facilities)
    total_definite_income = sum(f.definite_income or 0 for f in facilities)
    total_transferred_income = sum(f.transferred_income or 0 for f in facilities)
    total_insurance = sum(f.insurance_amount or 0 for f in facilities)
    total_tax = sum(f.tax_amount or 0 for f in facilities)
    total_net_payments = sum(f.remaining_balance or 0 for f in facilities)
    total_repayments = sum(f.total_payment or 0 for f in facilities)

    rows = [
        {
            "index": i + 1,
            "company_name": facility.shareholder.name,
            "start_date": facility.start_date.strftime("%Y/%m/%d"),
            "end_date": facility.end_date.strftime("%Y/%m/%d"),
            "num_cases": facility.num_cases if hasattr(facility, "num_cases") else 0,
            "amount_received": facility.amount_received or 0,
            "total_payment": facility.total_payment or 0,  # کل درآمد
            "added_value": facility.tax_amount or 0,  # ارزش افزوده
            "insurance": facility.insurance_amount or 0,  # بیمه
            "definite_income": facility.definite_income or 0,  # درآمد قطعی
            "transferred_income": facility.transferred_income or 0,  # درآمد انتقالی
            "net_payment": facility.remaining_balance or 0,  # خالص پرداختی
        }
        for i, facility in enumerate(facilities)
    ]

    context = {
        "year": today_jalali.year,
        "facilities": rows,
        "total_loans": total_loans,
        "total_definite_income": total_definite_income,
        "total_transferred_income": total_transferred_income,
        "total_insurance": total_insurance,
        "total_tax": total_tax,
        "total_net_payments": total_net_payments,
        "total_repayments": total_repayments,
    }

    return render(request, "admin/facility/financial_report.html", context)
