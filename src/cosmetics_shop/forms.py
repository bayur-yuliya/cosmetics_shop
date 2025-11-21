from django import forms
from django.contrib.auth.models import User

from cosmetics_shop.models import Client, DeliveryAddress, GroupProduct, Brand, Tag
from accounts.utils.validators import validate_phone_number


class ClientForm(forms.ModelForm):
    phone = forms.CharField(max_length=10, validators=[validate_phone_number])

    class Meta:
        model = Client
        fields = ["first_name", "last_name", "phone"]


class DeliveryAddressForm(forms.ModelForm):

    class Meta:
        model = DeliveryAddress
        fields = ["city", "street", "post_office"]


class ProductFilterForm(forms.Form):
    name = forms.CharField(required=False, label="Название содержит")

    group = forms.ModelMultipleChoiceField(
        widget=forms.CheckboxSelectMultiple,
        queryset=GroupProduct.objects.all(),
        initial=0,
        required=False,
    )

    brand = forms.ModelMultipleChoiceField(
        widget=forms.CheckboxSelectMultiple,
        queryset=Brand.objects.all(),
        initial=0,
        required=False,
    )

    tags = forms.ModelMultipleChoiceField(
        widget=forms.CheckboxSelectMultiple,
        queryset=Tag.objects.all(),
        initial=0,
        required=False,
    )

    min_price = forms.DecimalField(required=False, label="Min price")
    max_price = forms.DecimalField(required=False, label="Max price")


class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(label="Password", widget=forms.PasswordInput)
    password2 = forms.CharField(label="Repeat password", widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ("email",)

    def clean_password2(self):
        cd = self.cleaned_data
        if cd["password"] != cd["password2"]:
            raise forms.ValidationError("Passwords don't match.")
        return cd["password2"]
