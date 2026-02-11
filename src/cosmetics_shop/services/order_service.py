from typing import Any

from django.db import transaction
from django.db.models import Prefetch
from django.http import HttpRequest

from cosmetics_shop.models import (
    Cart,
    CartItem,
    Order,
    OrderItem,
    DeliveryAddress,
    Client,
    Product,
    OrderStatusLog,
)
from cosmetics_shop.services.cart_services import clear_cart_after_order
from cosmetics_shop.services.client_service import get_client
from utils.custom_types import AuthenticatedRequest


def get_cart(request: HttpRequest) -> Cart:
    if request.user.is_authenticated:
        cart, _ = Cart.objects.get_or_create(user=request.user)
    else:
        cart_id = request.session.get("cart_id")
        if cart_id:
            try:
                return Cart.objects.get(id=cart_id)
            except Cart.DoesNotExist:
                pass
        cart = Cart.objects.create()
        request.session["cart_id"] = cart.id
    return cart


def change_stock_product(product_code: int, count: int) -> None:
    product = Product.objects.get(code=product_code)
    if product.stock >= count:
        product.stock -= count
        product.save()
    else:
        raise ValueError("Товаров больше нет")


def create_order_from_cart(request: AuthenticatedRequest, address_id: int) -> Order:
    cart = get_cart(request)
    cart_items = CartItem.objects.select_related("product").filter(cart=cart)

    if not cart_items.exists():
        raise ValueError("Корзина пуста")

    try:
        client = get_client(request)
    except Client.DoesNotExist:
        raise ValueError("Клиент не найден")

    try:
        address = DeliveryAddress.objects.get(id=address_id, client=client)
    except DeliveryAddress.DoesNotExist:
        raise ValueError("Адрес не найден или не принадлежит клиенту")

    total_price = sum(item.product.price * item.quantity for item in cart_items)

    with transaction.atomic():
        full_name = f"{client.last_name} {client.first_name}"
        user_email = client.user.email if client.user and client.user.email else ""

        order = Order.objects.create(
            client=client,
            snapshot_name=full_name,
            snapshot_phone=client.phone,
            snapshot_email=user_email,
            snapshot_address=str(address),
            total_price=total_price,
        )

        order_items = [
            OrderItem(
                order=order,
                product=item.product,
                price=item.product.price,
                quantity=item.quantity,
                snapshot_product=item.product.name,
                snapshot_price=item.product.price,
                snapshot_quantity=item.quantity,
            )
            for item in cart_items
        ]

        for item in cart_items:
            if item.product.code and item.quantity:
                change_stock_product(item.product.code, item.quantity)

        OrderStatusLog.objects.create(order=order)
        OrderItem.objects.bulk_create(order_items)

        clear_cart_after_order(request)

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
