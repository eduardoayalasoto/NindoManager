from django import forms
from .models import Branch

from apps.common.form_styles import INPUT_CLASS


class BranchForm(forms.ModelForm):
    class Meta:
        model = Branch
        fields = ["name", "code", "address", "phone", "email", "is_active"]
        widgets = {
            "name": forms.TextInput(attrs={"class": INPUT_CLASS}),
            "code": forms.TextInput(attrs={"class": INPUT_CLASS}),
            "address": forms.Textarea(attrs={"class": INPUT_CLASS, "rows": 3}),
            "phone": forms.TextInput(attrs={"class": INPUT_CLASS}),
            "email": forms.EmailInput(attrs={"class": INPUT_CLASS}),
        }
