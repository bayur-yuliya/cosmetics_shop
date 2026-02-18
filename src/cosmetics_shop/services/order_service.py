from typing import Any

from django.db import transaction
from django.db.models import Prefetch

from cosmetics_shop.models import (
    Cart,
    CartItem,
    Order,
    OrderItem,
    Client,
    Product,
    OrderStatusLog,
)
from cosmetics_shop.utils.cart_utils import get_or_create_cart
from utils.custom_types import AuthenticatedRequest


def change_stock_product(product_code: int, count: int) -> None:
    product = Product.objects.get(code=product_code)
    if product.stock >= count:
        product.stock -= count
        product.save()
    else:
        raise ValueError("Товаров больше нет")


def clear_cart_after_order(cart: Cart) -> None:
    cart.cartitem_set.all().delete()


def create_order_from_cart(request: AuthenticatedRequest, address_id: int) -> Order:
    cart = get_or_create_cart(request)
    cart_items = CartItem.objects.select_related("product").filter(cart=cart)

    with transaction.atomic():
        # full_name = f"{client.last_name} {client.first_name}"
        # user_email = client.user.email if client.user and client.user.email else ""
        #
        order = Order.objects.create(
            #     client=client,
            #     snapshot_name=full_name,
            #     snapshot_phone=client.phone,
            #     snapshot_email=user_email,
            #     snapshot_address=str(address),
            #     total_price=total_price,
        )

        order_items = [
            OrderItem(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.price,
            )
            for item in cart_items
        ]

        for item in cart_items:
            if item.product.code and item.quantity:
                change_stock_product(item.product.code, item.quantity)

        OrderStatusLog.objects.create(order=order)
        OrderItem.objects.bulk_create(order_items)
        order.update_total_price()

        clear_cart_after_order(cart)

        if not request.user.is_authenticated:
            request.session.pop("cart_id", None)

    return order


def get_order_items_by_client(client: Client) -> list[dict[str, Any]]:
    status_prefetch = Prefetch(
        "status_log",
        queryset=OrderStatusLog.objects.order_by("-changed_at"),
        to_attr="order_statuses",
    )

    orders = (
        Order.objects.filter(client=client)
        .prefetch_related("items__product", status_prefetch)
        .order_by("-created_at")
    )
    order_items_data: list[dict[str, Any]] = []

    for order in orders:
        latest_status: OrderStatusLog | None = (
            order.order_statuses[0] if order.order_statuses else None
        )

        order_items_data.append(
            {
                "order": order,
                "items": order.items.all(),
                "latest_status": latest_status,
                "status_badge_class": (
                    latest_status.status_badge_class() if latest_status else "secondary"
                ),
            }
        )

    return order_items_data
