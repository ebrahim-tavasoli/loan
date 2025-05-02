from django import forms

from loan.model_fields import CommaSeparatedInput


class CommaSeparatedBaseForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if isinstance(field, forms.IntegerField):
                field.widget = CommaSeparatedInput()
