from django import forms
from facility import models
from django_jalali.forms import jDateField
from django_jalali.forms.widgets import jDateInput



class FacilityReportForm(forms.Form):
    facility_type = forms.ModelChoiceField(
        queryset=models.FacilityType.objects.all(),
        required=True,
        label="نوع تسهیلات",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    from_date = jDateField(
        required=True,
        label="از تاریخ",
        widget=jDateInput(attrs={
            'class': 'vDateField',
            'placeholder': 'از تاریخ',
            'autocomplete': 'off',
            'data-jdp': ''
        })
    )
    to_date = jDateField(
        required=True,
        label="تا تاریخ",
        widget=jDateInput(attrs={
            'class': 'vDateField',
            'placeholder': 'تا تاریخ',
            'autocomplete': 'off',
            'data-jdp': ''
        })
    )