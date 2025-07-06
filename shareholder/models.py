import jdatetime

from django.db import models
from django.db.models import Sum, Q, F
from django.db.models.functions import Coalesce
from django_jalali.db import models as jmodels

from facility import models as facility_models
from django_comma_integer_field import CommaIntegerField


class Shareholder(models.Model):
    SHAREHOLDER_TYPE_CHOICES = [
        ('natural', 'حقیقی'),
        ('legal', 'حقوقی'),
    ]
    
    shareholder_type = models.CharField(
        "نوع سهامدار", 
        max_length=10, 
        choices=SHAREHOLDER_TYPE_CHOICES,
        default='natural'
    )
    accounting_code = models.CharField("کد حسابداری", max_length=32, unique=True)
    
    # Common fields for both types
    name = models.CharField("نام/نام شرکت", max_length=255)
    phone = models.CharField("شماره تلفن", max_length=11)
    city = models.CharField("شهر", max_length=255)
    address = models.TextField("آدرس")
    
    # Fields for Natural shareholders
    melli_code = models.CharField("کد ملی", max_length=10, unique=True, null=True, blank=True)
    father_name = models.CharField("نام پدر", max_length=255, null=True, blank=True)
    birth_date = jmodels.jDateField("تاریخ تولد", null=True, blank=True)
    id_number = models.CharField("شماره شناسنامه", max_length=20, null=True, blank=True)
    issued_by = models.CharField("صادره از", max_length=32, null=True, blank=True)
    job = models.CharField("شغل", max_length=32, null=True, blank=True)
    
    # Fields for Legal shareholders
    company_registration_number = models.CharField("شماره ثبت شرکت", max_length=32, null=True, blank=True)
    economic_code = models.CharField("کد اقتصادی", max_length=14, null=True, blank=True)
    registration_date = jmodels.jDateField("تاریخ ثبت شرکت", null=True, blank=True)
    legal_representative_name = models.CharField("نام نماینده قانونی", max_length=255, null=True, blank=True)
    legal_representative_melli_code = models.CharField("کد ملی نماینده قانونی", max_length=10, null=True, blank=True)
    company_type = models.CharField("نوع شرکت", max_length=100, null=True, blank=True)
    
    created_at = jmodels.jDateTimeField("تاریخ ثبت", auto_now_add=True)
    updated_at = jmodels.jDateTimeField("تاریخ ویرایش", auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.get_shareholder_type_display()})"

    def clean(self):
        from django.core.exceptions import ValidationError
        
        if self.shareholder_type == 'natural':
            # Validate required fields for natural shareholders
            if not self.melli_code:
                raise ValidationError({'melli_code': 'کد ملی برای سهامداران حقیقی الزامی است.'})
            if not self.father_name:
                raise ValidationError({'father_name': 'نام پدر برای سهامداران حقیقی الزامی است.'})
            if not self.birth_date:
                raise ValidationError({'birth_date': 'تاریخ تولد برای سهامداران حقیقی الزامی است.'})
        
        elif self.shareholder_type == 'legal':
            # Validate required fields for legal shareholders
            if not self.company_registration_number:
                raise ValidationError({'company_registration_number': 'شماره ثبت شرکت برای سهامداران حقوقی الزامی است.'})
            if not self.economic_code:
                raise ValidationError({'economic_code': 'کد اقتصادی برای سهامداران حقوقی الزامی است.'})
            if not self.legal_representative_name:
                raise ValidationError({'legal_representative_name': 'نام نماینده قانونی برای سهامداران حقوقی الزامی است.'})

    @property
    def is_natural(self):
        return self.shareholder_type == 'natural'
    
    @property
    def is_legal(self):
        return self.shareholder_type == 'legal'
    
    @property
    def display_identifier(self):
        """Returns the main identifier based on shareholder type"""
        if self.is_natural:
            return self.melli_code
        else:
            return self.company_registration_number

    class Meta:
        verbose_name = "سهامدار"
        verbose_name_plural = "سهامداران"
        constraints = [
            models.UniqueConstraint(
                fields=['melli_code'],
                condition=Q(shareholder_type='natural', melli_code__isnull=False),
                name='unique_melli_code_for_natural'
            ),
            models.UniqueConstraint(
                fields=['company_registration_number'],
                condition=Q(shareholder_type='legal', company_registration_number__isnull=False),
                name='unique_registration_number_for_legal'
            ),
            models.UniqueConstraint(
                fields=['economic_code'],
                condition=Q(shareholder_type='legal', economic_code__isnull=False),
                name='unique_economic_code_for_legal'
            ),
        ]

    @property
    def total_shares(self):
        return self.share_set.aggregate(total_shares=Coalesce(Sum("amount"), 0))[
            "total_shares"
        ]

    @property
    def total_shares_number(self):
        return self.share_set.aggregate(total_shares=Coalesce(Sum("share_number"), 0))[
            "total_shares"
        ]

    @property
    def total_debt(self):
        debt = 0
        for i in self.facilityrequest_set.filter(is_approved=True):
            debt += i.facility.total_debt
        return debt

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
                facility__facility_request__shareholder=self,
                created_at__gte=current_year_start,
                created_at__lt=next_year_start,
            ).aggregate(total=Sum("amount"))["total"]
            or 0
        )
        return total

    total_shares.fget.short_description = "مبلغ سهام"
    total_shares_number.fget.short_description = "تعداد سهام"
    total_facilities_in_year.fget.short_description = "مجموع تسهیلات در سال مالی جاری"
    total_repayments_in_year.fget.short_description = (
        "مجموع بازپرداخت‌ها در سال مالی جاری"
    )
    is_natural.fget.short_description = "سهامدار حقیقی"
    is_legal.fget.short_description = "سهامدار حقوقی"
    display_identifier.fget.short_description = "شناسه اصلی"


class Share(models.Model):
    shareholder = models.ForeignKey(
        Shareholder, on_delete=models.CASCADE, verbose_name="سهامدار"
    )
    share_number = CommaIntegerField("تعداد سهام", default=0,)
    amount = CommaIntegerField("مبلغ سهام")
    description = models.TextField("زمینه فعالیت", null=True, blank=True,)
    created_at = jmodels.jDateTimeField("تاریخ ثبت", auto_now_add=True)
    updated_at = jmodels.jDateTimeField("تاریخ ویرایش", auto_now=True)

    def __str__(self):
        return f"{self.shareholder.name} - {self.amount}"

    class Meta:
        verbose_name = "سهام"
        verbose_name_plural = "سهام ها"
