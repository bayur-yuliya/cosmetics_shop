import logging

from django.db import transaction
from django.db.models import F, Sum
from django.shortcuts import get_object_or_404

from cosmetics_shop.models import Cart, CartItem, Product

logger = logging.getLogger(__name__)


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
    logger.debug(f"Add to cart: cart_id={cart.id}, product_code={product_code}")

    product = get_object_or_404(Product, code=product_code)

    with transaction.atomic():
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart, product=product, defaults={"quantity": 1}
        )

        if created:
            logger.info(
                f"Product added to cart: cart_id={cart.id}," f" product_id={product.id}"
            )
        else:
            if cart_item.quantity < product.stock:
                cart_item.quantity = F("quantity") + 1
                cart_item.save()
                logger.info(
                    f"Product quantity increased: cart_id={cart.id},"
                    f" product_id={product.id}"
                )
            else:
                logger.warning(
                    f"Stock limit reached: product_id={product.id},"
                    f" stock={product.stock}"
                )


def remove_product_from_cart(cart: Cart, product_code: int) -> None:
    logger.debug(f"Remove one item: cart_id={cart.id}, product_code={product_code}")

    with transaction.atomic():
        updated = CartItem.objects.filter(
            cart=cart, product__code=product_code, quantity__gt=1
        ).update(quantity=F("quantity") - 1)

        if updated:
            logger.info(
                f"Product quantity decreased: cart_id={cart.id},"
                f" product_code={product_code}"
            )


def delete_product_from_cart(cart: Cart, product_id: int) -> None:
    logger.debug(f"Delete product: cart_id={cart.id}, product_id={product_id}")

    product = get_object_or_404(Product, pk=product_id)

    deleted, _ = CartItem.objects.filter(cart=cart, product=product).delete()

    logger.info(
        f"Product removed from cart: cart_id={cart.id},"
        f" product_id={product_id},"
        f" deleted={deleted}"
    )


def delete_cart(cart: Cart) -> None:
    logger.debug(f"Clearing cart: cart_id={cart.id}")

    deleted, _ = CartItem.objects.filter(cart=cart).delete()

    logger.info(f"Cart cleared: cart_id={cart.id}, items_deleted={deleted}")


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
    logger.debug(f"Clearing cart after order: cart_id={cart.id}")

    deleted, _ = cart.cart_items.all().delete()

    logger.info(f"Cart cleared after order: cart_id={cart.id}, items_deleted={deleted}")
