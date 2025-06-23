from django import forms

from cosmetics_shop.models import Client, DeliveryAddress


class ClientForm(forms.ModelForm):

    class Meta:
        model = Client
        fields = ['full_name', 'email', 'phone']


class DeliveryAddressForm(forms.ModelForm):

    class Meta:
        model = DeliveryAddress
        fields = ['city', 'street', 'post_office']
