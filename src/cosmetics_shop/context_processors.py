import logging

from django.contrib.auth.forms import UserCreationForm
from django.db.models import Sum
from django.urls import resolve

from cosmetics_shop.models import CartItem, Client
from cosmetics_shop.utils.cart_utils import get_cart

logger = logging.getLogger(__name__)


def cart_item_count(request):
    current_app = resolve(request.path).app_name

    if current_app == "staff":
        return {}

    cart = get_cart(request)

    if not cart:
        return {"cart_item_count": 0}

    count = (
        CartItem.objects.filter(cart=cart).aggregate(total=Sum("quantity"))["total"]
        or 0
    )

    logger.debug("Cart item count calculated", extra={"count": count})

    return {"cart_item_count": count}


def register_form(request):
    return {"form_register": UserCreationForm()}


# need cache
def is_pending_deletion_client(request):
    if request.user.is_authenticated:
        try:
            client = Client.objects.get(user=request.user)

            logger.debug(
                "Fetched client deletion status",
                extra={
                    "user_id": request.user.id,
                    "is_pending": client.is_pending_deletion,
                },
            )

            return {
                "is_pending_deletion": client.is_pending_deletion,
                "deletion_scheduled_date": client.deletion_scheduled_date,
            }
        except Client.DoesNotExist:
            logger.warning(
                "Client not found for user", extra={"user_id": request.user.id}
            )
            return {"is_pending_deletion": None}
    else:
        return {"is_pending_deletion": None}
