from email.policy import default

import jdatetime
from decimal import Decimal

from django.db import models
from django.db.models import Sum
from django.db.models.functions import Coalesce
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.utils import timezone

from tinymce.models import HTMLField
from django_jalali.db import models as jmodels


class FacilitySetting(models.Model):
    name = models.CharField(max_length=255, unique=True)
    fa_name = models.CharField("نام", max_length=255)
    value = models.CharField("مقدار")
    created_at = jmodels.jDateTimeField("تاریخ ثبت", auto_now_add=True)
    updated_at = jmodels.jDateTimeField("تاریخ ویرایش", auto_now=True)

    class Meta:
        verbose_name = "تنظیمات"
        verbose_name_plural = "تنظیمات"

    def __str__(self):
        return self.fa_name

    ######
    @classmethod
    def current_fiscal_year_start_date(cls):
        try:
            fiscal_year_start = cls.objects.get(name="fiscal_year_start").value
            month, day = map(int, fiscal_year_start.split("/"))
            if not (1 <= month <= 12 and 1 <= day <= 31):  # Basic validation
                raise ValueError("Month or day out of valid range.")
            today = jdatetime.date.today()
            year = today.year if today.month >= month else today.year - 1
            return jdatetime.date(year, month, day)
        except cls.DoesNotExist:
            raise ValueError("Fiscal year start setting is not defined.")
        except (ValueError, IndexError):
            raise ValueError(
                "Invalid format for fiscal year start. Expected 'month/day' (e.g., '4/1')."
            )

    @classmethod
    def current_fiscal_year_days(cls):
        start_date = cls.current_fiscal_year_start_date()
        end_date = jdatetime.date(start_date.year + 1, start_date.month, start_date.day)
        return (end_date - start_date).days


class FacilityType(models.Model):
    name = models.CharField("نام", max_length=25, unique=True)
    created_at = jmodels.jDateTimeField("تاریخ ثبت", auto_now_add=True)
    updated_at = jmodels.jDateTimeField("تاریخ ویرایش", auto_now=True)

    class Meta:
        verbose_name = "نوع تسهیلات"
        verbose_name_plural = "نوع تسهیلات"

    def __str__(self):
        return self.name


class FacilityRequest(models.Model):
    shareholder = models.ForeignKey(
        "shareholder.Shareholder", on_delete=models.CASCADE, verbose_name="سهامدار"
    )
    facility_type = models.ForeignKey(
        FacilityType, on_delete=models.CASCADE, verbose_name="نوع تسهیلات"
    )
    amount = models.IntegerField("مبلغ", default=0)
    repayment_duration = models.IntegerField("بازپرداخت به ماه", default=1)
    request_description = models.TextField("توحیجات طرح", blank=True, null=True)
    response_description = models.TextField("توضیحات هیات مدیره", blank=True, null=True)
    is_approved = models.BooleanField("تایید شده", default=False)
    response_file = models.FileField("فایل نتیجه", upload_to="فایل نتیجه", blank=True, null=True)
    response_date = jmodels.jDateTimeField("تاریخ پاسخ هیات مدیره", default=None, null=True, blank=True)
    created_at = jmodels.jDateTimeField("تاریخ در خواست", auto_now_add=True)
    updated_at = jmodels.jDateTimeField("تاریخ ویرایش", auto_now=True)  

    class Meta:
        verbose_name = "درخواست تسهیلات"
        verbose_name_plural = "درخواست تسهیلات"

    def __str__(self):
        return f"{self.shareholder.name} - {self.facility_type.name}"

    def save(self, *args, **kwargs):
        if self.response_file is not None:
            self.response_date = timezone.now()
        super(FacilityRequest, self).save(*args, **kwargs)
    
    def amount_in_letter(self):
        from num2fawords import words
        return words(self.amount)


class Facility(models.Model):
    facility_request = models.OneToOneField(
        FacilityRequest, on_delete=models.CASCADE, verbose_name="درخواست تسهیلات"
    )
    amount = models.IntegerField("مبلغ دریافتی", default=0)
    interest_rate = models.DecimalField(
        "درصد سود", max_digits=5, decimal_places=2, null=True, blank=True, default=0.0
    )
    insurance_rate = models.DecimalField(
        "درصد بیمه", max_digits=7, decimal_places=4, null=True, blank=True, default=0.0
    )
    tax_rate = models.DecimalField(
        "درصد مالیات", max_digits=7, decimal_places=4, null=True, blank=True, default=0.0
    )
    delay_penalty_rate = models.DecimalField("درصد نرخ جریمه تاخیر", max_digits=5, decimal_places=2, default=0.0)
    start_date = jmodels.jDateField("تاریخ پرداخت")
    end_date = jmodels.jDateField("تاریخ سر رسید")
    purchase_item = models.CharField("برای خرید", max_length=255, blank=True, null=True)
    for_target = models.CharField(
        "برای تامین بخشی از", max_length=255, blank=True, null=True
    )
    power_of_attorney_number = models.CharField(
        "شماره وکالت نامه", max_length=255, blank=True, null=True
    )
    power_of_attorney_date = jmodels.jDateField(
        "تاریخ وکالت نامه", blank=True, null=True
    )
    power_of_attorney_file = models.FileField("وکالت نامه", upload_to="power_of_attorney_file", blank=True, null=True)
    description = models.TextField("توضیحات", blank=True, null=True)
    is_settled = models.BooleanField("تسویه شده", default=False)
    created_at = jmodels.jDateTimeField("تاریخ ثبت", auto_now_add=True)
    updated_at = jmodels.jDateTimeField("تاریخ ویرایش", auto_now=True)

    class Meta:
        verbose_name = "تسهیلات"
        verbose_name_plural = "تسهیلات"

    def __str__(self):
        return f"{self.facility_request.shareholder.name} - {self.amount}"

    @property
    def is_overdue(self) -> bool:
        return self.total_debt > 0 and self.end_date < jdatetime.date.today()

    @property
    def delay_repayment_penalty(self):
        if not self.is_overdue or self.amount is None or self.end_date is None:
            return 0
        penalty_rate = self.delay_penalty_rate
        debt = self.total_debt
        current_year_start = FacilitySetting.current_fiscal_year_start_date()
        delay_start = max(self.end_date, current_year_start)
        delay_days = (jdatetime.date.today() - delay_start).days
        penalty = debt * penalty_rate * delay_days // 100
        return penalty if penalty > 0 else 0

    @property
    def facility_days(self):
        if self.start_date is None or self.end_date is None:
            return 0
        return (self.end_date - self.start_date).days

    @property
    def profit_yearly(self):
        if self.amount is None or self.interest_rate is None:
            return 0
        return self.amount * self.interest_rate // 100

    @property
    def profit(self):
        if (
            self.amount is None
            or self.interest_rate is None
            or self.facility_days == 0
        ):
            return 0
        days_of_year = FacilitySetting.current_fiscal_year_days()
        return self.profit_yearly / days_of_year * self.facility_days

    @property
    def insurance_amount(self):
        if self.amount is None or self.insurance_rate is None:
            return 0
        return self.amount * self.insurance_rate // 100

    @property
    def tax_amount(self):  # ارزش افزوده
        if self.amount is None or self.tax_rate is None:
            return 0
        return self.amount * self.tax_rate // 100

    @property
    def definite_days(self):
        fiscal_year_start = FacilitySetting.current_fiscal_year_start_date()
        if self.start_date is None or self.end_date is None:
            return 0
        next_fiscal_year_start = jdatetime.date(
            fiscal_year_start.year + 1, fiscal_year_start.month, fiscal_year_start.day
        )
        if (
            self.start_date >= fiscal_year_start
            and self.end_date <= next_fiscal_year_start
        ):
            return (self.end_date - self.start_date).days
        else:
            return (next_fiscal_year_start - self.start_date).days

    @property
    def transferred_days(self):
        return self.facility_days - self.definite_days

    @property
    def definite_income(self):  # درآمد قطعی
        fiscal_year_start = FacilitySetting.current_fiscal_year_start_date()
        if self.start_date is None or self.end_date is None:
            return 0
        next_fiscal_year_start = jdatetime.date(
            fiscal_year_start.year + 1, fiscal_year_start.month, fiscal_year_start.day
        )
        if (
            self.start_date >= fiscal_year_start
            and self.end_date <= next_fiscal_year_start
        ):
            return self.profit
        else:
            facility_days_of_current_year = (
                next_fiscal_year_start - self.start_date
            ).days
            return self.profit / self.facility_days * facility_days_of_current_year

    @property
    def transferred_income(self):  # درآمد انتقالی
        fiscal_year_start = FacilitySetting.current_fiscal_year_start_date()
        if self.start_date is None or self.end_date is None:
            return 0
        next_fiscal_year_start = jdatetime.date(
            fiscal_year_start.year + 1, fiscal_year_start.month, fiscal_year_start.day
        )
        if (
            self.start_date >= fiscal_year_start
            and self.end_date <= next_fiscal_year_start
        ):
            return 0
        else:
            facility_days_of_current_year = (
                next_fiscal_year_start - self.start_date
            ).days
            return (self.profit / self.facility_days) * (
                self.facility_days - facility_days_of_current_year
            )

    @property
    def total_deductions(self):  # جمع کسورات
        if (
            self.amount is None
            or self.insurance_rate is None
            or self.tax_amount is None
            or self.interest_rate is None
        ):
            return 0
        return int(self.insurance_amount + self.tax_amount + self.profit)

    @property
    def total_payment(self):
        if self.amount is None or self.total_deductions is None:
            return 0
        return self.amount - self.total_deductions

    @property
    def total_debt(self):
        if self.amount is None:
            return 0
        total_repaid = self.facility_repayments.aggregate(
            total_paid=Coalesce(Sum("amount"), 0)
        )["total_paid"]
        return max(self.amount - total_repaid, 0)

    @property
    def delay_repayment_penalty(self):
        if self.amount is None or self.end_date is None or not self.is_overdue:
            return 0
        penalty_rate = Decimal(
            FacilitySetting.objects.get(
                name="rate_of_facility_delay_repayment_penalty_daily"
            ).value
        )
        debt = self.total_debt
        current_year_start = FacilitySetting.current_fiscal_year_start_date()
        delay_start = max(self.end_date, current_year_start)
        delay_days = (jdatetime.date.today() - delay_start).days
        penalty = debt * penalty_rate * delay_days // 100
        return penalty if penalty > 0 else 0

    facility_days.fget.short_description = "روزهای تسهیلات"
    delay_repayment_penalty.fget.short_description = "جریمه تاخیر"
    profit_yearly.fget.short_description = "سود سالانه"
    profit.fget.short_description = "سود حاصل از این تسهیلات"
    insurance_amount.fget.short_description = "مبلغ بیمه"
    tax_amount.fget.short_description = "مبلغ مالیات"
    definite_income.fget.short_description = "درآمد قطعی"
    transferred_income.fget.short_description = "درآمد انتقالی"
    total_deductions.fget.short_description = "جمع کسورات"
    total_payment.fget.short_description = "مجموع پرداختی"
    definite_days.fget.short_description = "روزهای قطعی"
    transferred_days.fget.short_description = "روزهای انتقالی"
    total_debt.fget.short_description = "بدهی کل"
    is_overdue.fget.short_description = "تاخر در پرداخت بدهی"


class FacilityRepayment(models.Model):
    facility = models.ForeignKey(
        Facility,
        on_delete=models.CASCADE,
        related_name="facility_repayments",
        verbose_name="تسهیلات",
    )
    amount = models.IntegerField("مبلغ دریافتی", default=0)
    created_at = jmodels.jDateTimeField("تاریخ ثبت", auto_now_add=True)
    updated_at = jmodels.jDateTimeField("تاریخ ویرایش", auto_now=True)

    class Meta:
        verbose_name = "سر رسید تسهیلات"
        verbose_name_plural = "سر رسید تسهیلات"

    def __str__(self):
        return f"{self.facility.facility_request.shareholder.name} - {self.amount}"


class Guarantor(models.Model):
    facility = models.ForeignKey(
        "Facility",
        on_delete=models.CASCADE,
        related_name="guarantors",
        verbose_name="تسهیلات",
    )
    name = models.CharField("نام ضامن", max_length=255)
    father_name = models.CharField("نام پدر", max_length=255, blank=True, null=True)
    id_number = models.CharField("شماره شناسنامه", max_length=20, blank=True, null=True)
    national_id = models.CharField("کد ملی", max_length=10, unique=True)
    issued_by = models.CharField("محل صدور", max_length=255, blank=True, null=True)
    address = models.TextField("آدرس")
    phone = models.CharField("شماره تلفن", max_length=11)

    def __str__(self):
        return f"{self.name} - {self.national_id}"

    class Meta:
        verbose_name = "ضامن"
        verbose_name_plural = "ضامنین"