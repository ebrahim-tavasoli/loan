import jdatetime

from decimal import Decimal
from django.db import models
from django.db.models import Sum
from django.db.models.functions import Coalesce
from django.dispatch import receiver
from django.db.models.signals import post_save
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
    name = models.CharField(max_length=255, unique=True)
    fa_name = models.CharField("نام", max_length=255)
    percentage = models.DecimalField(
        "درصد سهام به تسهیلات", max_digits=3, decimal_places=2
    )
    rate = models.DecimalField("درصد سود", max_digits=3, decimal_places=2)
    created_at = jmodels.jDateTimeField("تاریخ ثبت", auto_now_add=True)
    updated_at = jmodels.jDateTimeField("تاریخ ویرایش", auto_now=True)

    class Meta:
        verbose_name = "نوع تسهیلات"
        verbose_name_plural = "نوع تسهیلات"

    def __str__(self):
        return self.fa_name


class Facility(models.Model):
    shareholder = models.ForeignKey(
        "shareholder.Shareholder", on_delete=models.CASCADE, verbose_name="سهامدار"
    )
    facility_type = models.ForeignKey(
        FacilityType, on_delete=models.CASCADE, verbose_name="نوع تسهیلات"
    )
    total_shares = models.BigIntegerField("میزان سهام", null=True, blank=True)
    amount = models.BigIntegerField("مبلغ", null=True, blank=True)
    amount_received = models.BigIntegerField("مبلغ دریافتی")
    interest_rate = models.DecimalField(
        "درصد سود", max_digits=5, decimal_places=2, null=True, blank=True
    )
    insurance_rate = models.DecimalField(
        "درصد بیمه", max_digits=7, decimal_places=4, null=True, blank=True
    )
    tax_rate = models.DecimalField(
        "درصد مالیات", max_digits=7, decimal_places=4, null=True, blank=True
    )
    start_date = jmodels.jDateField("تاریخ پرداخت")
    end_date = jmodels.jDateField("تاریخ سر رسید")
    purchase_item = models.CharField("برای خرید", max_length=255, blank=True, null=True)
    for_target = models.CharField("برای تامین بخشی از", max_length=255, blank=True, null=True)
    power_of_attorney_number = models.CharField("شماره وکالت نامه", max_length=255, blank=True, null=True)
    power_of_attorney_date = jmodels.jDateField("تاریخ وکالت نامه", blank=True, null=True)
    description = models.TextField("توضیحات", blank=True, null=True)
    created_at = jmodels.jDateTimeField("تاریخ ثبت", auto_now_add=True)
    updated_at = jmodels.jDateTimeField("تاریخ ویرایش", auto_now=True)
    is_overdue = models.BooleanField("بدهی", default=False)

    def save(self, *args, **kwargs):
        if self.pk:
            if self.end_date:
                self.is_overdue = (
                    self.total_debt > 0 and self.end_date < jdatetime.date.today()
                )
            else:
                self.is_overdue = False
        else:
            self.is_overdue = False

        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "تسهیلات"
        verbose_name_plural = "تسهیلات"

    def __str__(self):
        return f"{self.shareholder.name} - {self.amount}"

    @property
    def delay_repayment_penalty(self):
        if not self.is_overdue or self.amount_received is None or self.end_date is None:
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

    @property
    def facility_days(self):
        if self.start_date is None or self.end_date is None:
            return 0
        return (self.end_date - self.start_date).days

    @property
    def profit_yearly(self):
        if self.amount_received is None or self.interest_rate is None:
            return 0
        return self.amount_received * self.interest_rate // 100

    @property
    def profit(self):
        if (
            self.amount_received is None
            or self.interest_rate is None
            or self.facility_days == 0
        ):
            return 0
        days_of_year = FacilitySetting.current_fiscal_year_days()
        return self.profit_yearly / days_of_year * self.facility_days

    @property
    def insurance_amount(self):
        if self.amount_received is None or self.insurance_rate is None:
            return 0
        return self.amount_received * self.insurance_rate // 100

    @property
    def tax_amount(self):  # ارزش افزوده
        if self.amount_received is None or self.tax_rate is None:
            return 0
        return self.amount_received * self.tax_rate // 100

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
    def total_deductions(self):
        if (
            self.amount_received is None
            or self.insurance_rate is None
            or self.tax_amount is None
            or self.interest_rate is None
        ):
            return 0
        return (
            self.insurance_amount * self.amount_received
            + self.tax_amount * self.amount_received
            + self.interest_rate * self.amount_received
        )

    @property
    def total_payment(self):
        if self.amount_received is None or self.total_deductions is None:
            return 0
        return self.amount_received - self.total_deductions

    @property
    def remaining_balance(self):
        if self.amount_received is None or self.total_payment is None:
            return 0
        return self.amount_received - self.total_payment

    @property
    def total_debt(self):
        if self.amount_received is None:
            return 0
        total_repaid = self.facility_repayments.aggregate(
            total_paid=Coalesce(Sum("amount"), 0)
        )["total_paid"]
        return max(self.amount_received - total_repaid, 0)

    @property
    def delay_repayment_penalty(self):
        if self.amount_received is None or self.end_date is None or not self.is_overdue:
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
    remaining_balance.fget.short_description = "باقی‌مانده پرداختی"
    total_debt.fget.short_description = "بدهی کل"


class FacilityRepayment(models.Model):
    facility = models.ForeignKey(
        Facility,
        on_delete=models.CASCADE,
        related_name="facility_repayments",
        verbose_name="تسهیلات",
    )
    amount = models.BigIntegerField("مبلغ دریافتی")
    created_at = jmodels.jDateTimeField("تاریخ ثبت", auto_now_add=True)
    updated_at = jmodels.jDateTimeField("تاریخ ویرایش", auto_now=True)

    class Meta:
        verbose_name = "بازپرداخت تسهیلات"
        verbose_name_plural = "بازپرداخت تسهیلات"

    def __str__(self):
        return f"{self.facility.shareholder.name} - {self.amount}"


@receiver(post_save, sender=Facility)
def fill_facility_fields(sender, instance, created, **kwargs):
    if created:
        insurance_rate = (
            FacilitySetting.objects.get(name="insurance_rate").value
            if FacilitySetting.objects.get(name="insurance_enabled").value
            else 0
        )
        tax_rate = (
            FacilitySetting.objects.get(name="tax_rate").value
            if FacilitySetting.objects.get(name="tax_enabled").value
            else 0
        )
        instance.total_shares = instance.shareholder.total_shares
        instance.amount = (
            instance.facility_type.percentage * instance.shareholder.total_shares // 100
        )
        instance.interest_rate = instance.facility_type.rate
        instance.insurance_rate = insurance_rate
        instance.tax_rate = tax_rate
        instance.save()


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


class FinancialInstrument(models.Model):
    INSTRUMENT_TYPES = [
        ("check", "چک"),
        ("promissory_note", "سفته"),
    ]

    facility = models.ForeignKey(
        "Facility",
        on_delete=models.CASCADE,
        related_name="financial_instruments",
        verbose_name="تسهیلات",
    )
    instrument_type = models.CharField("نوع", max_length=20, choices=INSTRUMENT_TYPES)
    number = models.CharField("شماره", max_length=50, unique=True)
    amount = models.BigIntegerField("مبلغ")

    # Only for Checks
    account_number = models.CharField(
        "شماره حساب", max_length=50, blank=True, null=True
    )
    bank_name = models.CharField("نام بانک", max_length=255, blank=True, null=True)
    branch_name = models.CharField("نام شعبه", max_length=255, blank=True, null=True)
    bank_code = models.CharField("کد بانک", max_length=10, blank=True, null=True)
    owner_name = models.CharField("نام صاحب چک", max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.get_instrument_type_display()} شماره {self.number} - {self.amount} ریال"

    class Meta:
        verbose_name = "اسناد مالی"
        verbose_name_plural = "اسناد مالی"
