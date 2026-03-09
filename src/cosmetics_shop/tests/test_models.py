import pytest
from django.db import IntegrityError

from cosmetics_shop.models import (
    OrderItem,
    Order,
    DeliveryAddress,
    Client,
    Category,
    Status,
    OrderStatusLog,
    CartItem,
    Cart,
)
from .factories import user, category, group, brand, product


@pytest.mark.django_db
def test_slug_generated():
    category = Category.objects.create(name="Test Category")

    assert category.slug == "test-category"


@pytest.mark.django_db
def test_only_one_primary_address(user):
    client = Client.objects.create(
        user=user,
        first_name="John",
        last_name="Doe",
        phone="+380000000000",
        email="test@test.com",
    )

    address_1 = DeliveryAddress.objects.create(
        client=client, city="Odessa", street="Street", post_office="1", is_primary=True
    )
    address_2 = DeliveryAddress.objects.create(
        client=client, city="Odessa", street="Street", post_office="2", is_primary=True
    )
    address_1.refresh_from_db()

    assert address_2.is_primary is True
    assert address_1.is_primary is False


@pytest.mark.django_db
def test_product_code_generated(product):
    assert product.code is not None
    assert product.code >= 0


@pytest.mark.django_db
def test_order_snapshot(user):
    client = Client.objects.create(
        user=user,
        first_name="John",
        last_name="Doe",
        phone="+380000000000",
        email="client@test.com",
    )
    DeliveryAddress.objects.create(
        client=client,
        city="Some Sity",
        street="Street",
        post_office="12",
        is_primary=True,
    )
    order = Order.objects.create(client=client)

    assert order.snapshot_name == "John Doe"
    assert order.snapshot_phone == "+380000000000"
    assert order.snapshot_email == "client@test.com"


@pytest.mark.django_db
def test_order_total_price(product, user):
    client = Client.objects.create(
        user=user, phone="+380000000000", email="test@test.com"
    )

    order = Order.objects.create(client=client)
    OrderItem.objects.create(order=order, product=product, price=100.50, quantity=2)
    order.update_total_price()

    assert order.total_price == 201


@pytest.mark.django_db
def test_order_status_log(product, user):
    client = Client.objects.create(
        user=user, phone="+380000000000", email="test@test.com"
    )

    order = Order.objects.create(client=client)
    order.set_status(Status.COMPLETED, user=user)
    status_log = OrderStatusLog.objects.filter(order=order).first()

    assert status_log.status == Status.COMPLETED
    assert status_log.changed_by == user


@pytest.mark.django_db
def test_cart_item_unique(user, product):
    cart = Cart.objects.create(user=user)
    CartItem.objects.create(cart=cart, product=product, quantity=1)

    with pytest.raises(IntegrityError):
        CartItem.objects.create(cart=cart, product=product, quantity=2)
