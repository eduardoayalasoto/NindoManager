from django import forms
from .models import Role, UserRole
from apps.branches.models import Branch
from apps.users.models import User

from apps.common.form_styles import INPUT_CLASS


class RoleForm(forms.ModelForm):
    class Meta:
        model = Role
        fields = [
            "name", "description",
            "can_manage_users", "can_manage_branches", "can_manage_tasks",
            "can_view_all_branches", "can_view_reports", "can_view_activities",
        ]
        widgets = {
            "name": forms.TextInput(attrs={"class": INPUT_CLASS}),
            "description": forms.Textarea(attrs={"class": INPUT_CLASS, "rows": 3}),
        }


class UserRoleForm(forms.ModelForm):
    class Meta:
        model = UserRole
        fields = ["user", "role", "branch"]
        widgets = {
            "user": forms.Select(attrs={"class": INPUT_CLASS}),
            "role": forms.Select(attrs={"class": INPUT_CLASS}),
            "branch": forms.Select(attrs={"class": INPUT_CLASS}),
        }
