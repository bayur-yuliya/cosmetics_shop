from django.db import transaction
from django.db.models import F, Sum
from django.shortcuts import get_object_or_404

from cosmetics_shop.models import Cart, Product, CartItem


def get_id_products_in_cart(cart: Cart) -> list[int]:
    if not cart:
        return []

    cart_products = list(
        CartItem.objects.filter(cart=cart)
        .values_list("product_id", flat=True)
        .distinct()
    )
    return cart_products


def add_product_to_cart(cart: Cart, product_code: int) -> None:
    product = get_object_or_404(Product, code=product_code)

    with transaction.atomic():
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart, product=product, defaults={"quantity": 1}
        )
        if not created:
            if cart_item.quantity < product.stock:
                cart_item.quantity = F("quantity") + 1
                cart_item.save()


def remove_product_from_cart(cart: Cart, product_code: int) -> None:
    with transaction.atomic():
        CartItem.objects.filter(
            cart=cart, product__code=product_code, quantity__gt=1
        ).update(quantity=F("quantity") - 1)


def delete_product_from_cart(cart: Cart, product_id: int) -> None:
    product = get_object_or_404(Product, pk=product_id)
    CartItem.objects.filter(cart=cart, product=product).delete()


def delete_cart(cart: Cart) -> None:
    CartItem.objects.filter(cart=cart).delete()


def is_product_in_cart(cart: Cart, product_pk: int) -> bool:
    if not cart:
        return False
    return CartItem.objects.filter(cart=cart, product__pk=product_pk).exists()


def get_cart_total_price(cart_items):
    return (
        cart_items.aggregate(total_price=Sum(F("product__price") * F("quantity")))[
            "total_price"
        ]
        or 0
    )


def clear_cart_after_order(cart: Cart) -> None:
    cart.cart_items.all().delete()
