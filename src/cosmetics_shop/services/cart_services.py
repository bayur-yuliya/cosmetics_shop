from decimal import Decimal

from django.db import transaction
from django.db.models import QuerySet, F, Sum
from django.shortcuts import get_object_or_404

from cosmetics_shop.models import Cart, Product, CartItem


def get_id_products_in_cart(cart: Cart) -> set[int]:
    cart_products = set(
        CartItem.objects.filter(cart=cart).values_list("product_id", flat=True)
    )
    return cart_products


def add_product_to_cart(cart: Cart, product_code: int) -> None:
    with (transaction.atomic()):
        CartItem.objects.filter(
            cart=cart,
            product__code=product_code,
            quantity__gt=1
        ).update(quantity=F("quantity") + 1)


def remove_product_from_cart(cart: Cart, product_code: int) -> None:
    with transaction.atomic():
        CartItem.objects.filter(
            cart=cart,
            product__code=product_code,
            quantity__gt=1
        ).update(quantity=F("quantity") - 1)


def delete_product_from_cart(cart: Cart, product_id: int) -> None:
    product = get_object_or_404(Product, pk=product_id)
    CartItem.objects.filter(cart=cart, product=product).delete()


def delete_cart(cart: Cart) -> None:
    CartItem.objects.filter(cart=cart).delete()


def is_product_in_cart(cart: Cart, product_id: int) -> bool:
    return CartItem.objects.filter(cart=cart).exists(product__id=product_id)


def build_cart_state(cart, product_code: int | None = None, message=None):
    cart_items = (
        CartItem.objects
        .select_related("product")
        .filter(cart=cart)
    )

    total_quantity = (
        cart_items.aggregate(total=Sum("quantity"))["total"] or 0
    )

    total_price = (
        cart_items.aggregate(
            total=Sum(F("quantity") * F("product__price"))
        )["total"] or Decimal("0.00")
    )

    response = {
        "success": True,
        "count": total_quantity,
        "total_price": float(total_price),
        "message": message,
    }

    if product_code:
        product_item = cart_items.filter(product__code=product_code).first()

        if product_item:
            response.update({
                "product_code": product_code,
                "product_count": product_item.quantity,
                "product_total_price": float(
                    product_item.quantity * product_item.product.price
                ),
            })

    return response
