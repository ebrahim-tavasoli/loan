from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.contrib.admin import SimpleListFilter
from django.urls import reverse
from django.utils.html import format_html

from shareholder import models
from facility import models as facility_models


class ShareInline(admin.TabularInline):
    model = models.Share
    extra = 1


class ShareholderTypeFilter(SimpleListFilter):
    title = _("نوع سهامدار")
    parameter_name = "shareholder_type"

    def lookups(self, request, model_admin):
        return [
            ("natural", _("حقیقی")),
            ("legal", _("حقوقی")),
        ]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(shareholder_type=self.value())
        return queryset


class HasDebtFilter(SimpleListFilter):
    title = _("بدهکار")
    parameter_name = "has_debt"

    def lookups(self, request, model_admin):
        return [
            ("yes", _("بدهکاران")),
            ("no", _("بدون بدهی")),
        ]

    def queryset(self, request, queryset):
        if self.value() == "yes":
            return queryset.filter(
                facility__amount_received__gt=models.F(
                    "facility__facility_repayments__amount"
                )
            )
        elif self.value() == "no":
            return queryset.exclude(
                facility__amount_received__gt=models.F(
                    "facility__facility_repayments__amount"
                )
            )
        return queryset


@admin.register(models.Shareholder)
class ShareholderAdmin(admin.ModelAdmin):
    list_display = (
        "accounting_code",
        "name",
        "shareholder_type",
        "display_identifier",
        "total_shares",
        "total_shares_number",
        "total_debt",
        "total_facilities_in_year",
        "total_repayments_in_year",
        "has_debt",
        "view_contract_link",
    )
    search_fields = (
        "accounting_code", 
        "melli_code", 
        "company_registration_number", 
        "economic_code",
        "name", 
        "phone", 
        "address"
    )
    readonly_fields = (
        "total_shares",
        "total_debt",
        "is_natural",
        "is_legal",
        "created_at",
        "updated_at",
    )
    list_filter = (
        "shareholder_type",
        "created_at",
        ShareholderTypeFilter,
        HasDebtFilter,
    )
    
    fieldsets = (
        ("اطلاعات عمومی", {
            'fields': ('shareholder_type', 'accounting_code', 'name', 'phone', 'city', 'address')
        }),
        ("اطلاعات سهامدار حقیقی", {
            'fields': ('melli_code', 'father_name', 'birth_date', 'id_number', 'issued_by', 'job'),
            'classes': ('collapse',),
        }),
        ("اطلاعات سهامدار حقوقی", {
            'fields': ('company_registration_number', 'economic_code', 'registration_date', 
                      'legal_representative_name', 'legal_representative_melli_code', 'company_type'),
            'classes': ('collapse',),
        }),
        ("اطلاعات سیستم", {
            'fields': ('total_shares', 'total_debt', 'is_natural', 'is_legal'),
            'classes': ('collapse',),
        }),
    )

    inlines = [ShareInline,]

    class Media:
        js = ["admin/js/jquery.init.js", "admin/js/autocomplete.js"]

    def view_contract_link(self, obj):
        url = reverse("shareholder:shareholder_contract", args=[obj.id])
        return format_html('<a href="{}" target="_blank">مشاهده گواهی</a>', url)
    view_contract_link.short_description = "گواهی سهام"


    def total_delay_penalty_display(self, obj):
        return int(obj.total_delay_penalty)
    total_delay_penalty_display.short_description = "مجموع جریمه تأخیر"

    def total_debt(self, obj):
        return obj.total_debt
    total_debt.short_description = _("کل بدهی سهامدار")

    def has_debt(self, obj):
        return obj.has_debt

    has_debt.boolean = True
    has_debt.short_description = _("بدهکار")


@admin.register(models.Share)
class ShareAdmin(admin.ModelAdmin):
    list_display = ("shareholder", "amount", "get_created_date", "get_updated_date")
    search_fields = ("shareholder__name", "amount")
    autocomplete_fields = ("shareholder",)

    def get_created_date(self, obj):
        return obj.created_at.date()

    get_created_date.short_description = "تاریخ ثبت"

    def get_updated_date(self, obj):
        return obj.updated_at.date()

    get_updated_date.short_description = "تاریخ ویرایش"

    class Media:
        js = ["admin/js/jquery.init.js", "admin/js/autocomplete.js"]
