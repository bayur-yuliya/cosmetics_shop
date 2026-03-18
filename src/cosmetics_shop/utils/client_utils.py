from django.http import HttpRequest
from django.utils import timezone

from cosmetics_shop.forms import ClientForm, DeliveryAddressForm
from cosmetics_shop.models import Client, DeliveryAddress


def get_client(request: HttpRequest) -> Client | None:
    if request.user.is_authenticated:
        try:
            return Client.objects.get(user=request.user)
        except Client.DoesNotExist:
            return None
    else:
        return None


def process_delivery_data(
    request: HttpRequest, client=None, last_address=None
) -> DeliveryAddress | None:
    form = ClientForm(request.POST, instance=client)
    form_delivery = DeliveryAddressForm(request.POST, instance=last_address)

    if form.is_valid() and form_delivery.is_valid():
        new_client = form.save(commit=False)

        if request.user.is_authenticated:
            new_client.user = request.user
            new_client.save()
        else:
            new_client.deletion_scheduled_date = timezone.now() + timezone.timedelta(
                days=365 * 3
            )
            request.session["client_data"] = form.cleaned_data
            request.session["address_data"] = form_delivery.cleaned_data

        new_client.save()

        address = form_delivery.save(commit=False)
        address.client = new_client
        address.save()
        return address
    return None
