from django.db import models

from django_jalali.db import models as jmodels


class Check(models.Model):
    facility = models.ForeignKey(
        "facility.Facility",
        on_delete=models.CASCADE,
        related_name="facility_check",
        verbose_name="تسهیلات",
    )
    number = models.CharField("شماره", max_length=50, unique=True)
    amount = models.IntegerField("مبلغ", default=0)
    account_number = models.CharField(
        "شماره حساب", max_length=50, blank=True, null=True
    )
    bank_name = models.CharField("نام بانک", max_length=255, blank=True, null=True)
    branch_name = models.CharField("نام شعبه", max_length=255, blank=True, null=True)
    bank_code = models.CharField("کد بانک", max_length=10, blank=True, null=True)
    owner_name = models.CharField("نام صاحب چک", max_length=255, blank=True, null=True)
    file = models.FileField("سفته", upload_to="promissory_notes")
    created_at = jmodels.jDateTimeField("زمان ایجاد", auto_now_add=True)

    def __str__(self):
        return f"{self.facility}-{self.amount}"

    class Meta:
        verbose_name = "چک"
        verbose_name_plural = "چک ها"

class PromissoryNote(models.Model):
    facility = models.ForeignKey(
        "facility.Facility",
        on_delete=models.CASCADE,
        related_name="facility_promissory_note",
        verbose_name="تسهیلات",
    )
    number = models.CharField("شماره", max_length=50, unique=True)
    amount = models.IntegerField("مبلغ", default=0)
    owner_name = models.CharField("نام صاحب سفته", max_length=255, blank=True, null=True)
    file = models.FileField("سفته", upload_to="promissory_notes")
    created_at = jmodels.jDateTimeField("زمان ایجاد", auto_now_add=True)

    def __str__(self):
        return f"{self.facility}-{self.amount}"

    class Meta:
        verbose_name = "سفته"
        verbose_name_plural = "سفته ها"

class PowerOfAttorney(models.Model):
    facility = models.ForeignKey(
        "facility.Guarantor",
        on_delete=models.CASCADE,
        related_name="facility_power_of_attorney",
    )
    number = models.CharField('شماره وکالت نامه', max_length=50, unique=True)
    date = jmodels.jDateTimeField('تاریخ وکالت نامه')
    file = models.FileField("فایل وکالت نامه", upload_to="power_of_attorney")
    created_at = jmodels.jDateTimeField("زمان ایجاد", auto_now_add=True)

    def __str__(self):
        return self.number

    class Meta:
        verbose_name = "وکالت نامه"
        verbose_name_plural = "وکالت نامه ها"