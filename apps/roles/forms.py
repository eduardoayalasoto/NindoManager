from django import forms
from .models import Role, UserRole
from apps.branches.models import Branch
from apps.users.models import User

INPUT_CLASS = "w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-black"


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
