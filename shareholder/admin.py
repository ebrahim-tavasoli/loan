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


class FacilityInline(admin.StackedInline):
    model = facility_models.Facility
    extra = 1
    fields = (
        "facility_type",
        "amount_received",
        "start_date",
        "end_date",
        "description",
    )

    def get_queryset(self, request):
        return facility_models.Facility.objects.none()


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
        "total_shares",
        "total_debt",
        "total_facilities_in_year",
        "total_repayments_in_year",
        "total_delay_penalty_display",
        "has_debt",
        "view_contract_link",
    )
    search_fields = ("accounting_code", "melli_code", "name", "phone", "address")
    readonly_fields = (
        "total_shares",
        "get_good_facility_amount",
        "get_force_facility_amount",
        "get_necessary_facility_amount",
        "total_delay_penalty_display",
        "total_debt",
    )
    list_filter = (
        "created_at",
        HasDebtFilter,
    )

    inlines = [ShareInline, FacilityInline]

    def view_contract_link(self, obj):
        url = reverse("shareholder:shareholder_contract", args=[obj.id])
        return format_html('<a href="{}" target="_blank">مشاهده گواهی</a>', url)

    view_contract_link.short_description = "گواهی سهام"

    def get_good_facility_amount(self, obj):
        return int(obj.good_facility_amount)

    get_good_facility_amount.short_description = "مبلغ تسهیلات قرض الحسنه"

    def get_force_facility_amount(self, obj):
        return int(obj.force_facility_amount)

    get_force_facility_amount.short_description = "مبلغ تسهیلات مضاربه"

    def get_necessary_facility_amount(self, obj):
        return int(obj.necessary_facility_amount)

    get_necessary_facility_amount.short_description = "مبلغ تسهیلات ضروری"

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
