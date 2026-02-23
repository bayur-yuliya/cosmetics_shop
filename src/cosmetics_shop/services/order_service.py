from typing import Any

from django.db import transaction
from django.db.models import Prefetch
from django.shortcuts import get_object_or_404

from cosmetics_shop.models import (
    Cart,
    CartItem,
    Order,
    OrderItem,
    Client,
    OrderStatusLog,
    DeliveryAddress,
)
from cosmetics_shop.services.product_service import change_stock_product
from cosmetics_shop.utils.cart_utils import get_cart
from utils.custom_exceptions import OutOfStockError
from utils.custom_types import AuthenticatedRequest


def clear_cart_after_order(cart: Cart) -> None:
    cart.cartitem_set.all().delete()


def create_order_from_cart(request: AuthenticatedRequest) -> Order:
    cart = get_cart(request)
    cart_items = CartItem.objects.select_related("product").filter(cart=cart)
    client_data = request.session.get("client_data", {})
    address_data = request.session.get("address_data", {})

    if cart.user:
        client = get_object_or_404(Client, user=cart.user)
        full_name = f"{client.last_name} {client.first_name}"
        user_email = client.email
        phone = client.phone
        primary_address = DeliveryAddress.objects.filter(client=client, is_primary=True)
        address = str(primary_address) if primary_address else "Адрес не указан"
    else:
        if not client_data or not address_data:
            raise ValueError("Данные для доставки отсутствуют")

        client = None
        full_name = f"{client_data['last_name']} {client_data['first_name']}"
        user_email = client_data["email"]
        phone = client_data["phone"]
        address = f"{address_data['city']}, {address_data['street']}, {address_data['post_office']}"

    with transaction.atomic():
        order = Order.objects.create(
            client=client,
            snapshot_name=full_name,
            snapshot_phone=phone,
            snapshot_email=user_email,
            snapshot_address=address,
        )

        order_items = [
            OrderItem(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.price,
                snapshot_product=item.product.name,
            )
            for item in cart_items
        ]

        for item in cart_items:
            if item.product.code and item.quantity:
                try:
                    change_stock_product(item.product.code, item.quantity)
                except ValueError:
                    raise OutOfStockError(f"Товара {item.product.name} недостаточно")

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
        .prefetch_related("order_items__product", status_prefetch)
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
                "items": order.order_items.all(),
                "latest_status": latest_status,
                "status_badge_class": (
                    latest_status.status_badge_class() if latest_status else "secondary"
                ),
            }
        )

    return order_items_data
