from django import forms

from accounts.utils.validators import validate_phone_number
from cosmetics_shop.models import Brand, Client, DeliveryAddress, GroupProduct, Tag


class ClientForm(forms.ModelForm):
    phone = forms.CharField(
        label="Номер телефона: ", max_length=10, validators=[validate_phone_number]
    )

    class Meta:
        model = Client
        fields = ["first_name", "last_name", "phone", "email"]
        labels = {
            "first_name": "Имя: ",
            "last_name": "Фамилия: ",
        }


class DeliveryAddressForm(forms.ModelForm):
    class Meta:
        model = DeliveryAddress
        fields = ["city", "post_office"]
        labels = {
            "city": "Город: ",
            "post_office": "Почтовое отделение: ",
        }
        widgets = {
            "city": forms.TextInput(
                attrs={
                    "class": "form-control np-city-input",
                    "placeholder": "Начните вводить город...",
                    "autocomplete": "off",
                }
            ),
            "post_office": forms.Select(
                attrs={
                    "class": "form-control np-warehouse-select",
                }
            ),
        }


class PaymentForm(forms.Form):
    method = forms.ChoiceField(
        choices=[
            ("card", "Онлайн"),
            ("cash", "При получении"),
        ],
        widget=forms.RadioSelect,
    )


class ProductFilterForm(forms.Form):
    name = forms.CharField(
        label="Название содержит",
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )

    group = forms.ModelMultipleChoiceField(
        label="Группа",
        widget=forms.CheckboxSelectMultiple,
        queryset=GroupProduct.objects.all(),
        initial=0,
        required=False,
    )

    brand = forms.ModelMultipleChoiceField(
        label="Бренды",
        widget=forms.CheckboxSelectMultiple,
        queryset=Brand.objects.all(),
        initial=0,
        required=False,
    )

    tags = forms.ModelMultipleChoiceField(
        label="Теги",
        widget=forms.CheckboxSelectMultiple,
        queryset=Tag.objects.all(),
        initial=0,
        required=False,
    )

    min_price = forms.DecimalField(
        required=False,
        label="Минимальная цена",
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    max_price = forms.DecimalField(
        required=False,
        label="Максимальная цена",
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
