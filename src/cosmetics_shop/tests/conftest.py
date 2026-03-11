import pytest

from ..models import Category, GroupProduct, Brand, Product, Tag, Client
from accounts.models import CustomUser


@pytest.fixture
def user(db):
    return CustomUser.objects.create_user(email="test@test.com", password="12345678")


@pytest.fixture
def client(user):
    return Client.objects.create(
        user=user,
        first_name="John",
        last_name="Doe",
        phone="+380000000000",
        email="test@test.com",
    )


@pytest.fixture
def category(db):
    return Category.objects.create(name="Test Category")


@pytest.fixture
def group(category):
    return GroupProduct.objects.create(name="Test Group", category=category)


@pytest.fixture
def category2(db):
    return Category.objects.create(name="Test Category 2")


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
    product1 = Product.objects.create(
        name="Гипоаллергенная тушь для объема, оттенок 1",
        group=group,
        brand=brand,
        price=150,
        description="Test1",
        stock=5,
    )
    product2 = Product.objects.create(
        name="Гипоаллергенная тушь для объема, оттенок 2",
        group=group2,
        brand=brand,
        price=100.50,
        description="Test2",
        stock=10,
    )
    product3 = Product.objects.create(
        name="Гипоаллергенная тушь для объема, оттенок 3",
        group=group2,
        brand=brand,
        price=210.50,
        description="Test3",
        stock=0,
    )
    product4 = Product.objects.create(
        name="Гипоаллергенная тушь для объема, оттенок 4",
        group=group,
        brand=brand,
        price=310.50,
        description="Test4",
        stock=0,
    )
    return [product1, product2, product3, product4]


@pytest.fixture(autouse=True)
def mock_env(mocker):
    from django.contrib.sites.models import Site

    Site.objects.get_or_create(id=1, defaults={"domain": "t.com", "name": "t"})
    return mocker.patch(
        "cosmetics_shop.models.reverse",
        side_effect=lambda name, kwargs: f"/{kwargs.get('slug', 'err')}/",
    )
