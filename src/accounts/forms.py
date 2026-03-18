from django import forms
from django.core.exceptions import ValidationError

from accounts.utils.validators import validate_phone_number
from cosmetics_shop.models import Client

from .utils.account_services import activate_user


class ClientCreationForm(forms.ModelForm):
    phone = forms.CharField(
        label="Номер телефона",
        max_length=13,
        validators=[validate_phone_number],
        required=False,
    )
    email = forms.EmailField(label="Email")

    class Meta:
        model = Client
        fields = ["first_name", "last_name", "email", "phone"]
        labels = {
            "first_name": "Имя",
            "last_name": "Фамилия",
        }

    def save(self, *args, **kwargs):
        instance = super().save(commit=False)
        if self.has_changed():
            instance.save()
        return instance


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

    def __init__(self, *args, token=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.token = token

    def get_user_and_password(self):
        if not self.token:
            return None

        password = self.cleaned_data["password1"]
        user = activate_user(self.token, password)

        return user, password
