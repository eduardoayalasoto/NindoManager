from django import forms
from .models import Task, TaskInstance, TaskChecklist

from apps.common.form_styles import INPUT_CLASS, SELECT_CLASS


class TaskForm(forms.ModelForm):
    recurring_days = forms.MultipleChoiceField(
        choices=Task.DAYS_OF_WEEK,
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Días de recurrencia",
    )

    class Meta:
        model = Task
        fields = [
            "title", "description", "module", "branch", "assigned_to",
            "priority", "estimated_duration", "is_recurring", "recurring_days",
            "due_date",
        ]
        widgets = {
            "title": forms.TextInput(attrs={"class": INPUT_CLASS}),
            "description": forms.Textarea(attrs={"class": INPUT_CLASS, "rows": 4}),
            "module": forms.Select(attrs={"class": SELECT_CLASS}),
            "branch": forms.Select(attrs={"class": SELECT_CLASS}),
            "assigned_to": forms.Select(attrs={"class": SELECT_CLASS}),
            "priority": forms.Select(attrs={"class": SELECT_CLASS}),
            "estimated_duration": forms.NumberInput(attrs={"class": INPUT_CLASS}),
            "due_date": forms.DateTimeInput(attrs={"class": INPUT_CLASS, "type": "datetime-local"}),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user and not user.is_superuser:
            branches = user.get_accessible_branches()
            self.fields["branch"].queryset = branches
        if self.instance.pk and self.instance.recurring_days:
            self.fields["recurring_days"].initial = self.instance.recurring_days

    def clean_recurring_days(self):
        days = self.cleaned_data.get("recurring_days", [])
        return list(days)


class TaskInstanceUpdateForm(forms.ModelForm):
    class Meta:
        model = TaskInstance
        fields = ["status", "notes", "assigned_to"]
        widgets = {
            "status": forms.Select(attrs={"class": SELECT_CLASS}),
            "notes": forms.Textarea(attrs={"class": INPUT_CLASS, "rows": 3}),
            "assigned_to": forms.Select(attrs={"class": SELECT_CLASS}),
        }


class TaskChecklistItemForm(forms.ModelForm):
    class Meta:
        model = TaskChecklist
        fields = ["item", "order"]
        widgets = {
            "item": forms.TextInput(attrs={"class": INPUT_CLASS}),
            "order": forms.NumberInput(attrs={"class": INPUT_CLASS}),
        }
