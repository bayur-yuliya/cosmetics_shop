from django.db.models import Sum
from django.urls import resolve

from cosmetics_shop.models import CartItem
from django.contrib.auth.forms import UserCreationForm

from cosmetics_shop.utils.cart_utils import get_cart


def cart_item_count(request):
    current_app = resolve(request.path).app_name

    if current_app == 'staff':
        return {}

    cart = get_cart(request)

    if not cart:
        return {"cart_item_count": 0}

    count = (
            CartItem.objects
            .filter(cart=cart)
            .aggregate(total=Sum("quantity"))["total"]
            or 0
    )

    return {"cart_item_count": count}


def register_form(request):
    return {"form_register": UserCreationForm()}
