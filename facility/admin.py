from django.contrib import admin
from django.urls import path, reverse
from django.shortcuts import get_object_or_404
from django.utils.html import format_html
from django.http import HttpResponseRedirect
from decouple import strtobool
import jdatetime

from facility import models


@admin.register(models.FacilitySetting)
class FacilitySettingAdmin(admin.ModelAdmin):
    list_display = ("fa_name", "value")
    search_fields = ("fa_name",)
    readonly_fields = ("fa_name", "created_at", "updated_at")
    exclude = ("name",)


@admin.register(models.FacilityType)
class FacilityTypeAdmin(admin.ModelAdmin):
    list_display = ("fa_name", "percentage", "rate")
    search_fields = ("name", "percentage", "rate")
    readonly_fields = ("fa_name", "created_at", "updated_at")
    exclude = ("name",)


@admin.register(models.Facility)
class FacilityAdmin(admin.ModelAdmin):
    list_display = (
        "shareholder",
        "amount_received",
        "total_payment",
        "remaining_balance",
        "total_debt",
        "is_overdue",
        "delay_repayment_penalty",
        "interest_rate",
        "start_date",
        "end_date",
        "generate_contract_link",
        "generate_form4_link",
        "generate_financial_report",
    )
    readonly_fields = (
        "amount",
        "interest_rate",
        "insurance_rate",
        "tax_rate",
        "total_shares",
        "total_payment",
        "remaining_balance",
        "total_debt",
        "is_overdue",
        "created_at",
        "updated_at",
    )
    list_filter = ("start_date", "end_date", "facility_type", "is_overdue")

    search_fields = (
        "shareholder__name",
        "shareholder__member_id",
        "shareholder__melli_code",
        "amount",
        "interest_rate",
    )
    autocomplete_fields = ("shareholder",)

    inlines = [
        type(
            "FacilityRepaymentInline",
            (admin.TabularInline,),
            {
                "model": models.FacilityRepayment,
                "extra": 1,
            },
        ),
        type(
            "FinancialInstrumentInline",
            (admin.StackedInline,),
            {
                "model": models.FinancialInstrument,
                "extra": 1,
            },
        ),
    ]

    actions = ["generate_contract"]

    def generate_contract(self, request, queryset):
        """Admin action to generate contract for a selected Facility"""
        facility = queryset.first()
        return HttpResponseRedirect(
            reverse("facility:generate_contract", args=[facility.id])
        )

    generate_contract.short_description = "📝 مشاهده قرارداد"

    class Media:
        js = ["admin/js/jquery.init.js", "admin/js/autocomplete.js"]

    def generate_contract_link(self, obj):
        """Show a clickable link to generate contract in admin panel"""
        url = reverse("facility:generate_contract", args=[obj.id])
        return format_html('<a href="{}" target="_blank">📄 قرارداد</a>', url)

    def generate_form4_link(self, obj):
        """Show a clickable link to generate Form 4"""
        url = reverse("facility:generate_form4", args=[obj.id])
        return format_html('<a href="{}" target="_blank">📝 فرم ۴</a>', url)

    def generate_financial_report(self, obj):
        """Generate a financial report link dynamically based on the object's year."""
        if obj.start_date:
            jalali_year = jdatetime.date.fromgregorian(date=obj.start_date).year
            url = reverse("facility:financial_report", args=[jalali_year])
            return format_html('<a href="{}" target="_blank">📊 گزارش مالی</a>', url)
        return "..."

    generate_contract_link.short_description = "قرارداد"
    generate_form4_link.short_description = "فرم شماره ۴"
    generate_financial_report.short_description = "گزارش مالی"

    def get_tax_rate(self, obj):
        if strtobool(models.FacilitySetting.objects.get(name="tax_enabled").value):
            return models.FacilitySetting.objects.get(name="tax_rate").value
        return "-"

    def get_insurance_rate(self, obj):
        if strtobool(
            models.FacilitySetting.objects.get(name="insurance_enabled").value
        ):
            return models.FacilitySetting.objects.get(name="insurance_rate").value
        return "-"

    get_tax_rate.short_description = "درصد مالیات"
    get_insurance_rate.short_description = "درصد بیمه"

    def total_debt(self, obj):
        return obj.total_debt

    total_debt.short_description = "بدهی باقی‌مانده"


@admin.register(models.FacilityRepayment)
class FacilityRepaymentAdmin(admin.ModelAdmin):
    list_display = ("facility", "amount", "created_at")
    list_filter = ("created_at",)
    search_fields = (
        "facility__shareholder__name",
        "facility__shareholder__member_id",
        "facility__shareholder__melli_code",
        "amount",
    )
    readonly_fields = ("created_at", "updated_at")


@admin.register(models.Guarantor)
class GuarantorAdmin(admin.ModelAdmin):
    list_display = ("facility", "name", "national_id", "phone")
    search_fields = ("name", "national_id", "phone")
    list_filter = ("facility",)


@admin.register(models.FinancialInstrument)
class FinancialInstrumentAdmin(admin.ModelAdmin):
    list_display = (
        "facility",
        "instrument_type",
        "number",
        "amount",
        "bank_name",
        "owner_name",
    )
    list_filter = ("instrument_type", "bank_name")
    search_fields = ("number", "facility__shareholder__name", "owner_name")
