from django.contrib import messages
from django.db.models import QuerySet, Sum, F
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST

from cosmetics_shop.models import CartItem
from cosmetics_shop.services.cart_services import (
    get_or_create_cart,
    delete_cart,
    delete_product_from_cart,
)


def cart(request: HttpRequest) -> HttpResponse:
    cart_object = get_or_create_cart(request)
    cart_items: QuerySet[CartItem] = CartItem.objects.select_related("product").filter(
        cart=cart_object
    )
    total_price = (
        cart_items.aggregate(total_price=Sum(F("product__price") * F("quantity")))[
            "total_price"
        ]
        or 0
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
    delete_cart(request)
    return redirect("cart")


@require_POST
def cart_delete(request: HttpRequest) -> HttpResponse:
    product_id_row: str | None = request.POST.get("product_id")
    if product_id_row is not None:
        product_id = int(product_id_row)
        delete_product_from_cart(request, product_id)
    else:
        messages.error(request, "Не удалось удалить товар")
    return redirect("cart")
