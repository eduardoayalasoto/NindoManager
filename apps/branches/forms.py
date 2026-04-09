from django import forms
from .models import Branch

INPUT_CLASS = "w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-black"


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
