from django.contrib.auth.models import AnonymousUser
from django.db.models import Sum
from django.urls import resolve

from cosmetics_shop.models import CartItem, Client
from django.contrib.auth.forms import UserCreationForm

from cosmetics_shop.utils.cart_utils import get_cart


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

    return {"cart_item_count": count}


def register_form(request):
    return {"form_register": UserCreationForm()}


# need cache
def is_pending_deletion_client(request):
    if request.user.is_authenticated:
        try:
            client = Client.objects.get(user=request.user)
            return {
                "is_pending_deletion": client.is_pending_deletion,
                "deletion_scheduled_date": client.deletion_scheduled_date,
            }
        except Client.DoesNotExist:
            return {"is_pending_deletion": None}
    else:
        return {"is_pending_deletion": None}
