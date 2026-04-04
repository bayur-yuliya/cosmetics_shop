import logging

from django.contrib import messages
from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST

from cosmetics_shop.models import CartItem
from cosmetics_shop.services.cart_services import (
    delete_cart,
    delete_product_from_cart,
    get_cart_total_price,
)
from cosmetics_shop.utils.cart_utils import get_cart

logger = logging.getLogger(__name__)


def cart(request: HttpRequest) -> HttpResponse:
    logger.debug(f"Cart view accessed: user_id={getattr(request.user, 'id', None)}")

    cart_object = get_cart(request)
    cart_items: QuerySet[CartItem] = CartItem.objects.select_related("product").filter(
        cart=cart_object
    )
    total_price = get_cart_total_price(cart_items)

    logger.debug(
        f"Cart loaded: cart_id={cart_object.id if cart_object else None}"
        f", items={cart_items.count()}"
    )

    return render(
        request,
        "cosmetics_shop/cart.html",
        {
            "title": "Корзина",
            "cart_items": cart_items,
            "total_price": total_price,
        },
    )


def clean_cart(request: HttpRequest) -> HttpResponse:
    cart_obj = get_cart(request)
    if cart_obj:
        logger.info(f"User cleared cart: cart_id={cart_obj.id if cart_obj else None}")

        delete_cart(cart_obj)
        messages.success(request, "Корзина очищена")

    return redirect("cart")


@require_POST
def cart_delete(request: HttpRequest, product_code: int) -> HttpResponse:
    cart_obj = get_cart(request)
    if product_code is not None and cart_obj:
        logger.info(
            f"User deletes product from cart: cart_id={cart_obj.id},"
            f" product_code={product_code}"
        )

        product_code_row = int(product_code)
        delete_product_from_cart(cart_obj, product_code_row)
        messages.success(request, "Товар успешно удален")
    else:
        logger.warning("cart_delete called without product_code")
        messages.error(request, "Не удалось удалить товар")

    return redirect("cart")
