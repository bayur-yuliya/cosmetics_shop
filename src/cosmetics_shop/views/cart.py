from django.contrib import messages
from django.db.models import QuerySet, Sum, F
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST

from cosmetics_shop.models import CartItem
from cosmetics_shop.services.cart_services import (
    delete_cart,
    delete_product_from_cart, get_cart_total_price,
)
from cosmetics_shop.utils.cart_utils import get_cart


def cart(request: HttpRequest) -> HttpResponse:
    cart_object = get_cart(request)
    cart_items: QuerySet[CartItem] = CartItem.objects.select_related("product").filter(
        cart=cart_object
    )
    total_price = get_cart_total_price(cart_items)

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
    delete_cart(cart_obj)
    messages.success(request, "Корзина очищена")
    return redirect("cart")


@require_POST
def cart_delete(request: HttpRequest, product_id: int) -> HttpResponse:
    cart_obj = get_cart(request)
    if product_id is not None:
        product_id_row = int(product_id)
        delete_product_from_cart(cart_obj, product_id_row)
        messages.success(request, "Товар успешно удален")
    else:
        messages.error(request, "Не удалось удалить товар")
    return redirect("cart")
