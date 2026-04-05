import logging
from typing import Any

from django.db import transaction
from django.shortcuts import get_object_or_404

from cosmetics_shop.models import (
    Cart,
    CartItem,
    Client,
    DeliveryAddress,
    Order,
    OrderItem,
)
from cosmetics_shop.services.product_service import (
    change_stock_product,
    restore_stock_product,
)
from utils.custom_exceptions import OutOfStockError

logger = logging.getLogger(__name__)


@transaction.atomic
def update_order_from_cart(order, cart, client_data, address_data):
    logger.info(f"Updating order started: order_id={order.id}")

    old_items = order.order_items.all()
    for item in old_items:
        restore_stock_product(item.product.code, item.quantity)
    old_items.delete()

    city = client_data.get("city", order.snapshot_address)
    post_office = client_data.get("post_office", "")

    address = f"{city} {post_office}".strip()

    first_name = client_data.get("first_name", order.snapshot_name)
    last_name = client_data.get("last_name", "")

    order.snapshot_name = f"{first_name} {last_name}".strip()

    order.snapshot_phone = client_data.get("phone", order.snapshot_phone)
    order.snapshot_email = client_data.get("email", order.snapshot_email)
    order.snapshot_address = address
    order.cart = cart

    new_order_items = []
    cart_items = cart.cart_items.select_related("product")

    for item in cart_items:
        try:
            change_stock_product(item.product.code, item.quantity)
        except ValueError:
            logger.warning(f"Out of stock during update: product={item.product.name}")
            raise OutOfStockError(f"Товара {item.product.name} недостаточно")

        new_order_items.append(
            OrderItem(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.price,
                snapshot_product=item.product.name,
            )
        )

    OrderItem.objects.bulk_create(new_order_items)
    order.update_total_price()
    order.save()

    logger.info(f"Order updated successfully: order_id={order.id}")
    return order


def create_order_from_cart(cart: Cart, client_data, address_data) -> Order:
    logger.info(f"START create_order_from_cart: cart_id={cart.id}")

    cart_items = CartItem.objects.select_related("product").filter(cart=cart)

    if not cart_items.exists():
        logger.warning(f"Cart is empty: cart_id={cart.id}")
        raise ValueError("Корзина пуста")

    if cart.user:
        logger.debug(f"Authenticated user checkout: user_id={cart.user.id}")

        client = get_object_or_404(Client, user=cart.user)

        full_name = f"{client.last_name} {client.first_name}"
        user_email = client.email
        phone = client.phone

        primary_address = DeliveryAddress.objects.filter(
            client=client, is_primary=True
        ).first()

        address = str(primary_address) if primary_address else "Адрес не указан"

    else:
        logger.debug("Anonymous checkout")

        if not client_data or not address_data:
            logger.warning(
                "CHECKOUT_FAILED: Missing delivery data | "
                f"client_data={bool(client_data)} address_data={bool(address_data)}"
            )
            raise ValueError("Данные для доставки отсутствуют")

        client = None
        full_name = f"{client_data['last_name']} {client_data['first_name']}"
        user_email = client_data["email"]
        phone = client_data["phone"]

        address = f"{address_data['city']}, " f"{address_data['post_office']}"

    try:
        with transaction.atomic():
            logger.debug("Transaction started")

            order = Order.objects.create(
                client=client,
                cart=cart,
                snapshot_name=full_name,
                snapshot_phone=phone,
                snapshot_email=user_email,
                snapshot_address=address,
            )

            logger.info(f"Order created: order_id={order.id}")

            order_items = []

            for item in cart_items:
                logger.debug(
                    f"Processing item: product={item.product.name}, qty={item.quantity}"
                )

                if item.product.code and item.quantity:
                    try:
                        change_stock_product(item.product.code, item.quantity)
                    except ValueError:
                        logger.warning(
                            f"Out of stock: product={item.product.name}, "
                            f"requested={item.quantity}"
                        )
                        raise OutOfStockError(
                            f"Товара {item.product.name} недостаточно"
                        )

                order_items.append(
                    OrderItem(
                        order=order,
                        product=item.product,
                        quantity=item.quantity,
                        price=item.product.price,
                        snapshot_product=item.product.name,
                    )
                )

            OrderItem.objects.bulk_create(order_items)

            logger.debug(f"Order items created: count={len(order_items)}")

            order.update_total_price()
            order.save()

            logger.info(
                f"Order finalized: order_id={order.id}, total={order.total_price}"
            )

    except Exception as e:
        logger.exception(
            f"ERROR during order creation: cart_id={cart.id}, error={str(e)}"
        )
        raise

    return order


def get_order_items_by_client(client: Client) -> list[dict[str, Any]]:
    logger.info(f"Fetching orders for client_id={client.id}")

    orders = (
        Order.objects.filter(client=client)
        .prefetch_related("order_items")
        .order_by("-created_at")
    )

    logger.debug(f"Orders found: count={orders.count()}")

    order_items_data: list[dict[str, Any]] = []

    for order in orders:
        logger.debug(f"Processing order_id={order.id}")

        status_badge = order.status_badge_class()

        order_items_data.append(
            {
                "order": order,
                "items": order.order_items.all(),
                "latest_status": order.get_status_display(),
                "status_badge_class": (status_badge if status_badge else "secondary"),
            }
        )

    return order_items_data
