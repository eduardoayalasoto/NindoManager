from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, SetPasswordForm
from .models import User
from apps.roles.models import Role
from apps.branches.models import Branch

INPUT_CLASS = "w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-black text-sm"


class NindoLoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            "class": INPUT_CLASS,
            "placeholder": "Usuario",
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            "class": INPUT_CLASS,
            "placeholder": "Contraseña",
        })
    )


class UserCreateForm(UserCreationForm):
    class Meta:
        model = User
        fields = ["username", "email", "first_name", "last_name", "phone", "whatsapp_number", "whatsapp_notifications"]
        widgets = {
            f: forms.TextInput(attrs={"class": INPUT_CLASS})
            for f in ["username", "email", "first_name", "last_name", "phone", "whatsapp_number"]
        }


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["first_name", "last_name", "email", "phone", "whatsapp_number", "whatsapp_notifications", "avatar"]
        widgets = {
            f: forms.TextInput(attrs={"class": INPUT_CLASS})
            for f in ["first_name", "last_name", "email", "phone", "whatsapp_number"]
        }


class AdminUserUpdateForm(forms.ModelForm):
    roles = forms.ModelMultipleChoiceField(
        queryset=Role.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple,
        label="Roles",
    )
    branches = forms.ModelMultipleChoiceField(
        queryset=Branch.objects.filter(is_active=True),
        required=False,
        widget=forms.CheckboxSelectMultiple,
        label="Sucursales",
    )

    class Meta:
        model = User
        fields = [
            "username", "first_name", "last_name", "email",
            "phone", "whatsapp_number", "whatsapp_notifications", "is_active",
        ]
        widgets = {
            f: forms.TextInput(attrs={"class": INPUT_CLASS})
            for f in ["username", "first_name", "last_name", "email", "phone", "whatsapp_number"]
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            active_role_ids = list(
                self.instance.user_roles.filter(is_active=True)
                .values_list("role_id", flat=True).distinct()
            )
            active_branch_ids = list(
                self.instance.user_roles.filter(is_active=True)
                .values_list("branch_id", flat=True).distinct()
            )
            self.fields["roles"].initial = active_role_ids
            self.fields["branches"].initial = active_branch_ids


class PasswordResetEmailForm(forms.Form):
    email = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(attrs={
            "class": INPUT_CLASS,
            "placeholder": "tu@email.com",
        }),
    )


class NindoSetPasswordForm(SetPasswordForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs["class"] = INPUT_CLASS
