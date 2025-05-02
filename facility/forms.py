from django import forms
from loan.base_forms import CommaSeparatedBaseForm
from facility import models
from django_jalali.forms import jDateField
from django_jalali.forms.widgets import jDateInput


class FacilityRequestForm(CommaSeparatedBaseForm):

    class Meta:
        model = models.FacilityRequest
        fields = '__all__'
        

class FacilityForm(CommaSeparatedBaseForm):

    class Meta:
        model = models.Facility
        fields = '__all__'
        

class FacilityRepaymentForm(CommaSeparatedBaseForm):

    class Meta:
        model = models.FacilityRepayment
        fields = '__all__'


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