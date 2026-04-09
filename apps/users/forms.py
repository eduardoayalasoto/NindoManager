from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, AuthenticationForm
from .models import User


class NindoLoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            "class": "w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-black",
            "placeholder": "Usuario",
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            "class": "w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-black",
            "placeholder": "Contraseña",
        })
    )


class UserCreateForm(UserCreationForm):
    class Meta:
        model = User
        fields = ["username", "email", "first_name", "last_name", "phone", "whatsapp_number", "whatsapp_notifications"]
        widgets = {
            f: forms.TextInput(attrs={"class": "w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-black"})
            for f in ["username", "email", "first_name", "last_name", "phone", "whatsapp_number"]
        }


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["first_name", "last_name", "email", "phone", "whatsapp_number", "whatsapp_notifications", "avatar"]
        widgets = {
            f: forms.TextInput(attrs={"class": "w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-black"})
            for f in ["first_name", "last_name", "email", "phone", "whatsapp_number"]
        }
