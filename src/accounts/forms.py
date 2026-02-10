from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.core.exceptions import ValidationError

from cosmetics_shop.models import Client
from .models import CustomUser
from accounts.utils.validators import validate_phone_number


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ("email",)


class CustomAuthenticationForm(AuthenticationForm):
    username = forms.EmailField(label="Email")


class ClientCreationForm(forms.ModelForm):
    phone = forms.CharField(
        label="Номер телефона",
        max_length=10,
        validators=[validate_phone_number],
        required=False,
    )
    email = forms.EmailField(label="Email", disabled=True)

    class Meta:
        model = Client
        fields = ["first_name", "last_name", "email", "phone"]
        labels = {
            "first_name": "Имя",
            "last_name": "Фамилия",
        }


class SetInitialPasswordForm(forms.Form):
    password1 = forms.CharField(
        widget=forms.PasswordInput,
        label="Введите пароль",
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput,
        label="Повторное введение пароля",
    )

    def clean(self):
        cleaned_data = super().clean()

        if cleaned_data is None:
            return None

        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        if (password1 and password2) and (password1 != password2):
            raise ValidationError("Пароли не совпадают")

        return cleaned_data
