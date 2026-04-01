from typing import cast

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
            "email": "Контактный email клиента: ",
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
        queryset=GroupProduct.objects.none(),
        initial=0,
        required=False,
    )

    brand = forms.ModelMultipleChoiceField(
        label="Бренды",
        widget=forms.CheckboxSelectMultiple,
        queryset=Brand.objects.none(),
        initial=0,
        required=False,
    )

    tags = forms.ModelMultipleChoiceField(
        label="Теги",
        widget=forms.CheckboxSelectMultiple,
        queryset=Tag.objects.none(),
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

    def __init__(self, *args, **kwargs):
        products_qs = kwargs.pop("products_qs", None)
        hide_group = kwargs.pop("hide_group", False)
        hide_brand = kwargs.pop("hide_brand", False)
        super().__init__(*args, **kwargs)

        if hide_group and "group" in self.fields:
            del self.fields["group"]
        if hide_brand and "brand" in self.fields:
            del self.fields["brand"]

        if products_qs is not None:
            if "group" in self.fields:
                group_field = cast(forms.ModelMultipleChoiceField, self.fields["group"])

                group_field.queryset = GroupProduct.objects.filter(
                    products__in=products_qs
                ).distinct()

            if "brand" in self.fields:
                brand_field = cast(forms.ModelMultipleChoiceField, self.fields["brand"])

                brand_field.queryset = Brand.objects.filter(
                    products__in=products_qs
                ).distinct()

            if "tags" in self.fields:
                tags_field = cast(forms.ModelMultipleChoiceField, self.fields["tags"])

                tags_field.queryset = Tag.objects.filter(
                    products__in=products_qs
                ).distinct()

        else:
            group_field = cast(forms.ModelMultipleChoiceField, self.fields["group"])
            group_field.queryset = GroupProduct.objects.all()

            brand_field = cast(forms.ModelMultipleChoiceField, self.fields["brand"])
            brand_field.queryset = Brand.objects.all()

            tags_field = cast(forms.ModelMultipleChoiceField, self.fields["tags"])
            tags_field.queryset = Tag.objects.all()
