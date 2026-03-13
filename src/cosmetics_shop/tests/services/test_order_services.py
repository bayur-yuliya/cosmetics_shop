import pytest

from cosmetics_shop.models import CartItem, Order, OrderItem, Status
from cosmetics_shop.services.order_service import (
    create_order_from_cart,
    get_order_items_by_client,
)


@pytest.mark.django_db
def test_create_order_from_cart(cart, client, address, product):
    assert Order.objects.filter(client=client).count() == 0

    CartItem.objects.create(cart=cart, product=product, quantity=3)
    create_order_from_cart(cart, client, address)
    order = Order.objects.filter(client=client)

    assert order.count() == 1


@pytest.mark.django_db
def test_get_order_items_by_client(client, product):
    order = Order.objects.create(client=client)
    OrderItem.objects.create(order=order, product=product, price=150.50, quantity=3)
    client_order_items = get_order_items_by_client(client)
    items = client_order_items[0]["items"]
    item = items.first()

    assert client_order_items[0]["order"] == order

    assert items.count() == 1

    assert item.product == product
    assert item.quantity == 3

    assert client_order_items[0]["latest_status"] == Status.NEW
    assert client_order_items[0]["status_badge_class"] == "info"
