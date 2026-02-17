from django.http import HttpRequest

from cosmetics_shop.forms import ClientForm, DeliveryAddressForm
from cosmetics_shop.models import DeliveryAddress, Client


def get_client(request: HttpRequest) -> Client:
    if request.user.is_authenticated:
        return Client.objects.get(user=request.user)

    client_id = request.session.get("client_id")
    if client_id:
        try:
            return Client.objects.get(id=client_id)
        except Client.DoesNotExist:
            pass

    raise Client.DoesNotExist("Клиент не найден в профиле или сессии")


def process_delivery_data(
    request: HttpRequest, client, last_address
) -> DeliveryAddress | None:
    form = ClientForm(request.POST, instance=client)
    form_delivery = DeliveryAddressForm(request.POST, instance=last_address)

    if form.is_valid() and form_delivery.is_valid():
        new_client = form.save()
        if request.user.is_authenticated:
            new_client.user = request.user
            new_client.save()

        address = form_delivery.save(commit=False)
        address.client = new_client
        address.save()
        return address
    return None
