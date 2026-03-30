import logging

from django.http import HttpRequest
from django.utils import timezone

from cosmetics_shop.forms import ClientForm, DeliveryAddressForm
from cosmetics_shop.models import Client, DeliveryAddress

logger = logging.getLogger(__name__)


def get_client(request: HttpRequest) -> Client | None:
    if request.user.is_authenticated:
        try:
            client = Client.objects.get(user=request.user)
            logger.debug(f"Client found: user_id={request.user.id}")
            return client

        except Client.DoesNotExist:
            logger.warning(f"Client not found: user_id={request.user.id}")
            return None

    return None


def process_delivery_data(
    request: HttpRequest, client=None, last_address=None
) -> DeliveryAddress | None:
    form = ClientForm(request.POST, instance=client)
    form_delivery = DeliveryAddressForm(request.POST, instance=last_address)

    if form.is_valid() and form_delivery.is_valid():
        logger.info(
            f"Processing delivery data: user_id={getattr(request.user, 'id', None)}"
        )
        new_client = form.save(commit=False)

        if request.user.is_authenticated:
            new_client.user = request.user
        else:
            logger.debug("Anonymous checkout data stored in session")
            new_client.deletion_scheduled_date = timezone.now() + timezone.timedelta(
                days=365 * 3
            )
            request.session["client_data"] = form.cleaned_data
            request.session["address_data"] = {
                "city": form_delivery.cleaned_data.get("city"),
                "post_office": form_delivery.cleaned_data.get("post_office"),
            }

        new_client.save()

        address = form_delivery.save(commit=False)
        address.client = new_client
        address.save()
        return address
    return None
