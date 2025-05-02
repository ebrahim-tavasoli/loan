from django.contrib import admin

import django_jalali.admin as jadmin
from django_jalali.admin.filters import JDateFieldListFilter

from guarantees import models, forms


class BaseAdmin(admin.ModelAdmin):
    search_fields = (
        "facility",
        "facility__facility_request__shareholder__accounting_code"
        "facility__facility_request__shareholder__melli_code"
        "facility__facility_request__shareholder__name"
        "facility__facility_request__shareholder__id_number"
    )
    list_filter = (
        ('created_at', JDateFieldListFilter),
    )
    autocomplete_fields = ("facility",)

    class Media:
        js = ["admin/js/jquery.init.js", "admin/js/autocomplete.js"]


@admin.register(models.Check)
class CheckAdmin(BaseAdmin):
    form = forms.CheckForm


class CheckInline(admin.StackedInline):
    model = models.Check
    form = forms.CheckForm
    extra = 0


@admin.register(models.PowerOfAttorney)
class PowerOfAttorneyAdmin(BaseAdmin):
    pass


class PowerOfAttorneyInline(admin.StackedInline):
    model = models.PowerOfAttorney
    extra = 0


@admin.register(models.PromissoryNote)
class PromissoryNoteAdmin(BaseAdmin):
    form = forms.PromissoryNoteForm


class PromissoryNoteInline(admin.StackedInline):
    model = models.PromissoryNote
    form = forms.PromissoryNoteForm
    extra = 0
