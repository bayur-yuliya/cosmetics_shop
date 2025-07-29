from django import forms

from cosmetics_shop.models import Client, DeliveryAddress, GroupProduct, Brand


class ClientForm(forms.ModelForm):

    class Meta:
        model = Client
        fields = ["full_name", "email", "phone"]


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

    min_price = forms.IntegerField(required=False, label="Min price")
    max_price = forms.IntegerField(required=False, label="Max price")
