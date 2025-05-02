from django.contrib import admin
from django.urls import path, reverse
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.utils.html import format_html
import jdatetime
from facility import models, forms
from django.shortcuts import render, HttpResponseRedirect
import jdatetime
from guarantees import admin as guarantees_admin
from django_jalali.admin.filters import JDateFieldListFilter

# You need to import this for adding jalali calendar widget
import django_jalali.admin as jadmin


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
    list_display = ("name",)
    search_fields = ("name",)
    readonly_fields = ("created_at", "updated_at")


class GuarantorInline(admin.StackedInline):
    model = models.Guarantor
    extra = 0


class FacilityRepaymentInline(admin.TabularInline):
    model = models.FacilityRepayment
    form = forms.FacilityRepaymentForm
    extra = 1


@admin.register(models.FacilityRequest)
class FacilityRequestAdmin(admin.ModelAdmin):
    list_display = (
        "shareholder",
        "facility_type",
        "formatted_amount",
        "request_facility_form"
    )
    form = forms.FacilityRequestForm
    autocomplete_fields = ("shareholder", "facility_type")
    search_fields = (
        "shareholder",
        "shareholder__name",
        "facility_type__name",
        "facility_type",

    )
    readonly_fields = ("created_at", "updated_at", "response_date")

    class Media:
        js = [
            "admin/js/jquery.init.js",
            "admin/js/autocomplete.js",
            "facility/js/format_numbers.js"
        ]
        
    def request_facility_form(self, obj):
        url = reverse("facility:request_facility", args=[obj.id])
        return format_html('<a href="{}" target="_blank">چاپ</a>', url)
    request_facility_form.short_description = "پرینت درخواست"

    def formatted_amount(self, obj):
        return f"{obj.amount:,}"
    formatted_amount.short_description = 'مبلغ'

@admin.register(models.Facility)
class FacilityAdmin(admin.ModelAdmin):
    form = forms.FacilityForm
    list_display = (
        "get_shareholder",
        "formatted_amount",
        "total_debt",
        "interest_rate",
        "insurance_rate",
        "tax_rate",
        "is_settled",
        "is_overdue",
        "created_date",
        "generate_contract_link",
        "generate_form4_link",
    )
    readonly_fields = (
        "is_settled",
        "is_overdue",
        "created_at",
        "updated_at",
    )
    list_filter = (
        ("start_date", JDateFieldListFilter),
        ("end_date", JDateFieldListFilter),
        "facility_request__facility_type",
        OverDuePenaltyFilter,
        HasDebtFilter,
    )
    search_fields = (
        "facility_request",
        "facility_request__shareholder__name",
        "facility_request__shareholder__member_id",
        "facility_request__shareholder__melli_code",
        "amount",
        "interest_rate",
    )
    autocomplete_fields = ("facility_request",)

    inlines = [
        FacilityRepaymentInline,
        GuarantorInline,
        guarantees_admin.CheckInline,
        guarantees_admin.PromissoryNoteInline
    ]

    actions = ["generate_contract"]

    class Media:
        js = ["admin/js/jquery.init.js", "admin/js/autocomplete.js", "facility/js/format_numbers.js"]

    def generate_contract(self, request, queryset):
        """Admin action to generate contract for a selected Facility"""
        facility = queryset.first()
        return HttpResponseRedirect(
            reverse("facility:generate_contract", args=[facility.id])
        )
    generate_contract.short_description = "📝 مشاهده قرارداد"

    def generate_contract_link(self, obj):
        """Show a clickable link to generate contract in admin panel"""
        url = reverse("facility:generate_contract", args=[obj.id])
        return format_html('<a href="{}" target="_blank">📄 قرارداد</a>', url)
    generate_contract_link.short_description = "قرارداد"

    def generate_form4_link(self, obj):
        """Show a clickable link to generate Form 4"""
        url = reverse("facility:generate_form4", args=[obj.id])
        return format_html('<a href="{}" target="_blank">📝 فرم ۴</a>', url)
    generate_form4_link.short_description = "فرم شماره ۴"

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
            "facility_form": forms.FacilityReportForm()
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

    def total_debt(self, obj):
        return f"{obj.total_debt:,}"
    total_debt.short_description = "بدهی باقی‌مانده"

    @admin.display(description="تاخر در پرداخت بدهی", boolean=True)
    def is_overdue(self, obj):
        return not obj.is_overdue

    def formatted_amount(self, obj):
        return f"{obj.amount:,}"
    formatted_amount.short_description = 'مبلغ'
    
    def created_date(self, obj):
        return obj.created_at.strftime('%Y/%m/%d')
    created_date.short_description = 'تاریخ ایجاد'
    
    def get_shareholder(self, obj):
        return obj.facility_request.shareholder
    get_shareholder.short_description = 'سهامدار'


@admin.register(models.FacilityRepayment)
class FacilityRepaymentAdmin(admin.ModelAdmin):
    form = forms.FacilityRepaymentForm
    list_display = ("facility", "amount", "created_at")
    search_fields = (
        "facility__facility_request__shareholder__name",
        "facility__facility_request__shareholder__member_id",
        "facility__facility_request__shareholder__melli_code",
        "amount",
    )
    readonly_fields = ("created_at", "updated_at")

    autocomplete_fields = ("facility",)

    class Media:
        js = ["admin/js/jquery.init.js", "admin/js/autocomplete.js", "facility/js/format_numbers.js"]


@admin.register(models.Guarantor)
class GuarantorAdmin(admin.ModelAdmin):
    list_display = ("facility", "name", "national_id", "phone")
    search_fields = ("name", "national_id", "phone")
    list_filter = ("facility",)

    autocomplete_fields = ("facility",)

    class Media:
        js = ["admin/js/jquery.init.js", "admin/js/autocomplete.js"]
