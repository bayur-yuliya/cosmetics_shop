from decimal import Decimal

from django.db import transaction
from django.db.models import QuerySet, F
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


def calculate_cart_total(cart: Cart) -> Decimal | int:
    return sum(item.product.price * item.quantity for item in cart.cartitem_set.select_related('product').all())


def calculate_product_total_price(
    cart_items: QuerySet[CartItem], product_code: int
) -> Decimal:
    product_count: CartItem | None = cart_items.filter(
        product__code=product_code
    ).first()
    if product_count is not None:
        return product_count.quantity * product_count.product.price
    return Decimal(0.0)


def is_product_in_cart(cart: Cart, product_id: int) -> bool:
    return CartItem.objects.filter(cart=cart).exists(product__id=product_id)
