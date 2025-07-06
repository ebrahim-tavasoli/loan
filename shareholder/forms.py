from django import forms
from django.core.exceptions import ValidationError
from shareholder.models import Shareholder, Share


class ShareholderForm(forms.ModelForm):
    class Meta:
        model = Shareholder
        fields = '__all__'
        widgets = {
            'birth_date': forms.DateInput(attrs={'type': 'date'}),
            'registration_date': forms.DateInput(attrs={'type': 'date'}),
            'address': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['shareholder_type'].widget.attrs.update({'onchange': 'toggleShareholderFields()'})
        
        # Make all fields optional by default, we'll validate based on shareholder_type
        for field_name, field in self.fields.items():
            if field_name not in ['shareholder_type', 'accounting_code', 'name', 'phone', 'city', 'address']:
                field.required = False

    def clean(self):
        cleaned_data = super().clean()
        shareholder_type = cleaned_data.get('shareholder_type')
        
        if shareholder_type == 'natural':
            # Validate required fields for natural shareholders
            required_fields = ['melli_code', 'father_name', 'birth_date']
            for field in required_fields:
                if not cleaned_data.get(field):
                    field_label = self.fields[field].label or field
                    raise ValidationError({field: f'{field_label} برای سهامداران حقیقی الزامی است.'})
        
        elif shareholder_type == 'legal':
            # Validate required fields for legal shareholders
            required_fields = ['company_registration_number', 'economic_code', 'legal_representative_name']
            for field in required_fields:
                if not cleaned_data.get(field):
                    field_label = self.fields[field].label or field
                    raise ValidationError({field: f'{field_label} برای سهامداران حقوقی الزامی است.'})
        
        return cleaned_data

    class Media:
        js = ('shareholder/js/shareholder_form.js',)


class NaturalShareholderForm(ShareholderForm):
    """Form specifically for natural shareholders"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['shareholder_type'].initial = 'natural'
        self.fields['shareholder_type'].widget = forms.HiddenInput()
        
        # Hide legal shareholder fields
        legal_fields = [
            'company_registration_number', 'economic_code', 'registration_date',
            'legal_representative_name', 'legal_representative_melli_code', 'company_type'
        ]
        for field in legal_fields:
            if field in self.fields:
                self.fields[field].widget = forms.HiddenInput()


class LegalShareholderForm(ShareholderForm):
    """Form specifically for legal shareholders"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['shareholder_type'].initial = 'legal'
        self.fields['shareholder_type'].widget = forms.HiddenInput()
        
        # Hide natural shareholder fields
        natural_fields = [
            'melli_code', 'father_name', 'birth_date', 'id_number', 'issued_by', 'job'
        ]
        for field in natural_fields:
            if field in self.fields:
                self.fields[field].widget = forms.HiddenInput()


class ShareForm(forms.ModelForm):
    class Meta:
        model = Share
        fields = '__all__'
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }
