import jdatetime

from django.db import models
from django.db.models import Sum, Q, F
from django.db.models.functions import Coalesce
from django_jalali.db import models as jmodels

from facility import models as facility_models


class Shareholder(models.Model):
    accounting_code = models.CharField("کد حسابداری", max_length=32, unique=True)
    melli_code = models.CharField("کد ملی", max_length=10, unique=True)
    name = models.CharField("نام", max_length=255)
    father_name = models.CharField("نام پدر", max_length=255, blank=True, null=True)
    id_number = models.CharField("شماره شناسنامه", max_length=20, blank=True, null=True)
    phone = models.CharField("شماره تلفن", max_length=11)
    city = models.CharField("شهر", max_length=255, blank=True, null=True)
    address = models.TextField("آدرس")
    created_at = jmodels.jDateTimeField("تاریخ ثبت", auto_now_add=True)
    updated_at = jmodels.jDateTimeField("تاریخ ویرایش", auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "سهامدار"
        verbose_name_plural = "سهامداران"

    @property
    def total_shares(self):
        return self.share_set.aggregate(total_shares=Coalesce(Sum("amount"), 0))[
            "total_shares"
        ]

    @property
    def good_facility_amount(self):  # gharzolhasane
        return (
            facility_models.FacilityType.objects.get(name="good").percentage
            * self.total_shares
            // 100
        )

    @property
    def force_facility_amount(self):  # mozarebe
        return (
            facility_models.FacilityType.objects.get(name="force").percentage
            * self.total_shares
            // 100
        )

    @property
    def necessary_facility_amount(self):  # zaruri
        return (
            facility_models.FacilityType.objects.get(name="necessary").percentage
            * self.total_shares
            // 100
        )

    @property
    def total_delay_penalty(self):
        facilities = facility_models.Facility.objects.filter(shareholder=self)
        return sum(facility.delay_repayment_penalty for facility in facilities)

    @property
    def total_debt(self):
        return sum(facility.total_debt for facility in self.facility_set.all())

    @property
    def has_debt(self):
        return self.total_debt > 0

    @property
    def total_facilities_in_year(self):
        current_year_start = (
            facility_models.FacilitySetting.current_fiscal_year_start_date()
        )
        next_year_start = jdatetime.date(
            current_year_start.year + 1,
            current_year_start.month,
            current_year_start.day,
        )
        total = (
            self.facility_set.filter(
                start_date__gte=current_year_start, start_date__lt=next_year_start
            ).aggregate(total=Sum("amount_received"))["total"]
            or 0
        )
        return total

    @property
    def total_repayments_in_year(self):
        current_year_start = (
            facility_models.FacilitySetting.current_fiscal_year_start_date()
        )
        next_year_start = jdatetime.date(
            current_year_start.year + 1,
            current_year_start.month,
            current_year_start.day,
        )
        total = (
            facility_models.FacilityRepayment.objects.filter(
                facility__shareholder=self,
                created_at__gte=current_year_start,
                created_at__lt=next_year_start,
            ).aggregate(total=Sum("amount"))["total"]
            or 0
        )
        return total

    total_shares.fget.short_description = "میزان سهام"
    good_facility_amount.fget.short_description = "میزان قرض الحسنه قابل دریافت"
    force_facility_amount.fget.short_description = "میزان مضاربه قابل دریافت"
    necessary_facility_amount.fget.short_description = "میزان ضروری قابل دریافت"
    total_delay_penalty.fget.short_description = "مجموع جریمه تأخیر"
    total_facilities_in_year.fget.short_description = "مجموع تسهیلات در سال مالی جاری"
    total_repayments_in_year.fget.short_description = (
        "مجموع بازپرداخت‌ها در سال مالی جاری"
    )


class Share(models.Model):
    shareholder = models.ForeignKey(
        Shareholder, on_delete=models.CASCADE, verbose_name="سهامدار"
    )
    share_number = models.IntegerField("تعداد سهام", default=0,)
    amount = models.IntegerField("مقدار سهام")
    description = models.TextField("زمینه فعالیت", null=True, blank=True,)
    created_at = jmodels.jDateTimeField("تاریخ ثبت", auto_now_add=True)
    updated_at = jmodels.jDateTimeField("تاریخ ویرایش", auto_now=True)

    def __str__(self):
        return f"{self.shareholder.name} - {self.amount}"

    class Meta:
        verbose_name = "سهام"
        verbose_name_plural = "سهام ها"
