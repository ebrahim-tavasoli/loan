from django import forms

class CommaSeparatedInput(forms.TextInput):
    class Media:
        js = ('js/format_numbers.js',)

    def format_value(self, value):
        if value is not None:
            return f"{value:,}"
        return super().format_value(value)
