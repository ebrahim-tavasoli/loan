from django.contrib import admin
from django.urls import path, reverse
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.utils.html import format_html
from decouple import strtobool
import jdatetime
from facility import models
from django.shortcuts import render, HttpResponseRedirect
import jdatetime
from . import models


class OverDuePenaltyFilter(admin.SimpleListFilter):
    title = "جریمه دیرکرد"
    parameter_name = "payment_status"

    def lookups(self, request, model_admin):
        return (
            ("true", "دارد"),
            ("false", "ندارد"),
        )

    def queryset(self, request, queryset):
        value = self.value()
        if value == "true":
            return queryset.filter(
                end_date__lt=jdatetime.datetime.now(), is_settled=False
            )
        elif value == "false":
            return queryset.filter(
                Q(end_date__gte=jdatetime.datetime.now()) | Q(is_settled=True)
            )
        return queryset


class HasDebtFilter(admin.SimpleListFilter):
    title = "دارای بدهی"
    parameter_name = "has_debt"

    def lookups(self, request, model_admin):
        return (
            ("true", "دارد"),
            ("false", "ندارد"),
        )

    def queryset(self, request, queryset):
        value = self.value()
        if value == "true":
            return queryset.filter(is_settled=True)
        elif value == "false":
            return queryset.filter(is_settled=False)
        return queryset


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
        "total_debt",
        "is_overdue",
        "delay_repayment_penalty",
        "interest_rate",
        "start_date",
        "end_date",
        "generate_contract_link",
        "generate_form4_link",
    )
    readonly_fields = (
        "amount",
        "interest_rate",
        "insurance_rate",
        "tax_rate",
        "total_shares",
        "total_payment",
        "total_debt",
        "is_overdue",
        "created_at",
        "updated_at",
    )
    list_filter = (
        "start_date",
        "end_date",
        "facility_type",
        OverDuePenaltyFilter,
        HasDebtFilter,
    )
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

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                "financial-report/",
                self.admin_site.admin_view(self.generate_financial_report_view),
                name="facility_financial_report",
            ),
        ]
        return custom_urls + urls

    def generate_financial_report_view(self, request):
        """Custom view to select fiscal year and generate financial report"""
        if request.method == "POST":
            year = request.POST.get("year")
            if year:
                return HttpResponseRedirect(
                    reverse("facility:financial_report", args=[year])
                )

        # پیدا کردن سال‌های مالی موجود
        facilities = models.Facility.objects.all()
        years = sorted(set(f.start_date.year for f in facilities if f.start_date))
        current_year = jdatetime.date.today().year
        if current_year not in years:
            years.append(current_year)

        # تبدیل سال‌ها به بازه‌ها (مثل 1403-1404)
        year_ranges = [f"{year}-{year + 1}" for year in years]

        context = {
            "years": zip(years, year_ranges),
            "current_year": current_year,
        }
        return render(request, "admin/facility/financial_report_form.html", context)

    def changelist_view(self, request, extra_context=None):
        """Add financial report button to the changelist page"""
        extra_context = extra_context or {}
        extra_context["show_financial_report_button"] = True
        extra_context["financial_report_url"] = reverse(
            "admin:facility_financial_report"
        )
        return super().changelist_view(request, extra_context=extra_context)

    generate_contract_link.short_description = "قرارداد"
    generate_form4_link.short_description = "فرم شماره ۴"

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

    @admin.display(description="تاخر در پرداخت بدهی", boolean=True)
    def is_overdue(self, obj):
        return not obj.is_overdue


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
