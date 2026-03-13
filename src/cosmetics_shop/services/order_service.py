from typing import Any

from django.db import transaction
from django.shortcuts import get_object_or_404

from cosmetics_shop.models import (
    Cart,
    CartItem,
    Order,
    OrderItem,
    Client,
    DeliveryAddress,
)
from cosmetics_shop.services.cart_services import clear_cart_after_order
from cosmetics_shop.services.product_service import change_stock_product
from utils.custom_exceptions import OutOfStockError


def create_order_from_cart(cart: Cart, client_data, address_data) -> Order:
    cart_items = CartItem.objects.select_related("product").filter(cart=cart)

    if cart.user:
        client = get_object_or_404(Client, user=cart.user)
        full_name = f"{client.last_name} {client.first_name}"
        user_email = client.email
        phone = client.phone
        primary_address = DeliveryAddress.objects.filter(
            client=client, is_primary=True
        ).first()
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
        order.save()

        clear_cart_after_order(cart)

    return order


def get_order_items_by_client(client: Client) -> list[dict[str, Any]]:
    orders = (
        Order.objects.filter(client=client)
        .prefetch_related("order_items")
        .order_by("-created_at")
    )
    order_items_data: list[dict[str, Any]] = []

    for order in orders:
        status_badge = order.status_badge_class
        order_items_data.append(
            {
                "order": order,
                "items": order.order_items.all(),
                "latest_status": order.status,
                "status_badge_class": (status_badge if status_badge else "secondary"),
            }
        )

    return order_items_data
