import uuid
from decimal import Decimal

import pytest
from django.contrib.sessions.middleware import SessionMiddleware
from django.utils import timezone

from accounts.models import CustomUser

from ..models import (
    Brand,
    Cart,
    CartItem,
    Category,
    Client,
    DeliveryAddress,
    GroupProduct,
    Order,
    OrderItem,
    Payment,
    Product,
    Status,
    Tag,
)


@pytest.fixture
def user(db):
    return CustomUser.objects.create_user(email="test@test.com", password="12345678")


@pytest.fixture
def other_user(db):
    return CustomUser.objects.create_user(email="example@test.com", password="12345678")


@pytest.fixture
def client_obj(user):
    return Client.objects.create(
        user=user,
        first_name="John",
        last_name="Doe",
        phone="+380000000000",
        email="test@test.com",
    )


@pytest.fixture
def address(client_obj):
    return DeliveryAddress.objects.create(
        client=client_obj,
        city="Test City",
        post_office="1",
        is_primary=True,
    )


@pytest.fixture
def category(db):
    return Category.objects.create(name="Test Category")


@pytest.fixture
def category2(db):
    return Category.objects.create(name="Test Category 2")


@pytest.fixture
def group(category):
    return GroupProduct.objects.create(name="Test Group", category=category)


@pytest.fixture
def group2(category2):
    return GroupProduct.objects.create(name="Test Group 2", category=category2)


@pytest.fixture
def brand(db):
    return Brand.objects.create(name="Test Brand")


@pytest.fixture
def tag(db):
    return Tag.objects.create(name="Test Tag")


@pytest.fixture
def product(group, brand, tag):
    product = Product.objects.create(
        name="Test Product",
        group=group,
        brand=brand,
        price=100.50,
        description="Test description",
        stock=5,
    )
    product.tags.add(tag)
    return product


@pytest.fixture
def products(group, group2, brand):
    Product.objects.create(
        name="Гипоаллергенная тушь для объема, оттенок 1",
        group=group,
        brand=brand,
        price=150,
        description="Test1",
        stock=5,
    )
    Product.objects.create(
        name="Гипоаллергенная тушь для объема, оттенок 2",
        group=group2,
        brand=brand,
        price=100.50,
        description="Test2",
        stock=10,
    )
    Product.objects.create(
        name="Гипоаллергенная тушь для объема, оттенок 3",
        group=group2,
        brand=brand,
        price=210.50,
        description="Test3",
        stock=0,
    )
    Product.objects.create(
        name="Гипоаллергенная тушь для объема, оттенок 4",
        group=group,
        brand=brand,
        price=310.50,
        description="Test4",
        stock=0,
    )
    return Product.objects.all()


@pytest.fixture
def cart(user):
    return Cart.objects.create(user=user)


@pytest.fixture
def cart_with_one_item(user, product):
    cart = Cart.objects.create(user=user)
    CartItem.objects.create(cart=cart, product=product, quantity=1)
    return cart


@pytest.fixture
def cart_with_items(user, products):
    cart = Cart.objects.create(user=user)
    for product in products:
        CartItem.objects.create(cart=cart, product=product, quantity=1)
    return cart


@pytest.fixture(autouse=True)
def mock_env(mocker):
    from django.contrib.sites.models import Site

    Site.objects.get_or_create(id=1, defaults={"domain": "t.com", "name": "t"})
    return mocker.patch(
        "cosmetics_shop.models.reverse",
        side_effect=lambda name, kwargs: (
            f"/{list(kwargs.values())[0]}/" if kwargs else "/err/"
        ),
    )


def add_session(request):
    middleware = SessionMiddleware(lambda r: None)
    middleware.process_request(request)
    request.session.save()


@pytest.fixture
def order_factory(db):
    def create_order(**kwargs):
        data = {
            "status": Status.NEW,
            "created_at": timezone.now(),
            "code": uuid.uuid4(),
        }
        data.update(kwargs)
        return Order.objects.create(**data)

    return create_order


@pytest.fixture
def payment_factory(db):
    def create_payment(order, **kwargs):
        data = {
            "order": order,
            "status": Payment.PaymentStatus.PENDING,
            "method": Payment.PaymentMethod.CARD,
            "amount": Decimal(100.00),
        }
        data.update(kwargs)
        return Payment.objects.create(**data)

    return create_payment


@pytest.fixture
def order_item_factory(db):
    def create_item(order, product, **kwargs):
        data = {
            "order": order,
            "product": product,
            "quantity": 1,
            "price": Decimal(100.00),
        }
        data.update(kwargs)
        return OrderItem.objects.create(**data)

    return create_item
