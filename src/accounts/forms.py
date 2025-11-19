from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm

from cosmetics_shop.models import Client
from .models import CustomUser
from .validators import validate_phone_number


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ("email",)


class CustomAuthenticationForm(AuthenticationForm):
    username = forms.EmailField(label="Email")


class ClientCreationForm(forms.ModelForm):
    phone = forms.CharField(max_length=10, validators=[validate_phone_number])
    email = forms.EmailField(disabled=True)

    class Meta:
        model = Client
        fields = ["first_name", "last_name", "email", "phone"]


class AdminCreateUserForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ("email",)

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_unusable_password()
        user.is_active = False
        if commit:
            user.save()
        return user
