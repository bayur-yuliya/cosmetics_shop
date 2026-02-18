from django.http import HttpRequest

from cosmetics_shop.forms import ClientForm, DeliveryAddressForm
from cosmetics_shop.models import DeliveryAddress, Client


def get_client(request: HttpRequest) -> Client | None:
    if request.user.is_authenticated:
        try:
            return Client.objects.get(user=request.user)
        except Client.DoesNotExist:
            pass
    else:
        return None


def process_delivery_data(
    request: HttpRequest, client=None, initial=None, last_address=None
) -> DeliveryAddress | None:
    form = ClientForm(request.POST, instance=client)
    form_delivery = DeliveryAddressForm(request.POST, instance=last_address, initial=initial)

    if form.is_valid() and form_delivery.is_valid():
        # request.session["checkout_data"] = form.cleaned_data
        new_client = form.save()
        if request.user.is_authenticated:
            new_client.user = request.user
            new_client.save()

        address = form_delivery.save(commit=False)
        address.client = new_client
        address.save()
        return address
    return None
