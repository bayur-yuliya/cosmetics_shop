import pytest
from django.contrib.redirects.models import Redirect
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.utils.text import slugify

from cosmetics_shop.models import (
    OrderItem,
    Order,
    DeliveryAddress,
    Category,
    Status,
    OrderStatusLog,
    CartItem,
    Cart,
    Product,
)


@pytest.mark.django_db
def test_basic_redirect(mock_env):
    obj = Category.objects.create(name="Old", slug="old-slug")
    obj.slug = "new-slug"
    obj.save()

    assert Redirect.objects.filter(
        old_path="/old-slug/", new_path="/new-slug/"
    ).exists()


@pytest.mark.django_db
def test_chain_redirect_update(mock_env):
    Redirect.objects.create(site_id=1, old_path="/archive/", new_path="/old/")

    obj = Category.objects.create(name="Test Category", slug="old")
    obj.slug = "new"
    obj.save()

    assert Redirect.objects.get(old_path="/archive/").new_path == "/new/"


@pytest.mark.django_db
def test_no_change_no_redirect(mock_env):
    obj = Category.objects.create(name="Test Category", slug="test-category")
    obj.save()

    assert not Redirect.objects.filter(old_path="/test-category/").exists()


@pytest.mark.django_db
def test_slug_generated():
    category = Category.objects.create(name="Test Category")

    assert category.slug == "test-category"


@pytest.mark.django_db
def test_slug_generated_error():
    with pytest.raises(ValidationError, match="Слаг не уникален."):
        Category.objects.create(name="Test Category")
        Category.objects.create(name="Test-Category")


@pytest.mark.django_db
def test_slug_clean_error_warning():
    name = "Duplicate Name"
    Category.objects.create(name=name, slug=slugify(name))
    category = Category(name=name)

    with pytest.raises(ValidationError) as e:
        category.full_clean()

        assert "name" in e.value.message_dict
        assert e.value.message_dict["name"] == ["Такое название уже используется."]


@pytest.mark.django_db
def test_clean_empty_source_and_slug():
    with pytest.raises(ValidationError, match="Это поле не может быть пустым."):
        empty_obj = Category(name="", slug="")
        empty_obj.full_clean()


@pytest.mark.django_db
def test_only_one_primary_address(client):
    address_1 = DeliveryAddress.objects.create(
        client=client,
        city="Test City",
        street="Test Street",
        post_office="1",
        is_primary=True,
    )
    address_2 = DeliveryAddress.objects.create(
        client=client,
        city="Test City",
        street="Test Street",
        post_office="2",
        is_primary=True,
    )
    address_1.refresh_from_db()

    assert address_2.is_primary is True
    assert address_1.is_primary is False


@pytest.mark.django_db
def test_product_code_generated(product):
    assert product.code is not None
    assert product.code >= 0


@pytest.mark.django_db
def test_product_queryset_with_stock_order(
    products,
):
    qs = Product.objects.with_stock_order()
    stocks = [a.stock for a in qs]

    assert stocks == [10, 5, 0, 0] or stocks == [5, 10, 0, 0]


@pytest.mark.django_db
def test_product_queryset_for_catalog(
    category,
    group,
    brand,
    product,
):
    qs = Product.objects.for_catalog().first()

    assert qs.group.name == "Test Group"
    assert qs.brand.name == "Test Brand"
    assert qs.tags.first().name == "Test Tag"


@pytest.mark.django_db
def test_product_sof_delete(product):
    product.soft_delete()
    assert not product.is_active


@pytest.mark.django_db
def test_order_snapshot(client):
    DeliveryAddress.objects.create(
        client=client,
        city="Test City",
        street="Test Street",
        post_office="1",
        is_primary=True,
    )
    order = Order.objects.create(client=client)

    assert order.snapshot_name == "John Doe"
    assert order.snapshot_phone == "+380000000000"
    assert order.snapshot_email == "test@test.com"


@pytest.mark.django_db
def test_order_total_price(product, client):
    order = Order.objects.create(client=client)
    OrderItem.objects.create(order=order, product=product, price=100.50, quantity=2)
    order.update_total_price()

    assert order.total_price == 201


@pytest.mark.django_db
def test_order_status_log(product, client, user):
    order = Order.objects.create(client=client)
    order.set_status(Status.COMPLETED, user=user)
    status_log = OrderStatusLog.objects.filter(order=order).first()

    assert status_log.status == Status.COMPLETED
    assert status_log.status_badge_class() == "success"
    assert status_log.changed_by == user


@pytest.mark.django_db
def test_cart_item_unique(user, product):
    cart = Cart.objects.create(user=user)
    CartItem.objects.create(cart=cart, product=product, quantity=1)

    with pytest.raises(IntegrityError):
        CartItem.objects.create(cart=cart, product=product, quantity=2)
