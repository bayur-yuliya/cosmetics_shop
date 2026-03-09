import pytest
from ..models import Category, GroupProduct, Brand, Product
from accounts.models import CustomUser


@pytest.fixture
def user(db):
    return CustomUser.objects.create_user(email="test@test.com", password="12345678")


@pytest.fixture
def category(db):
    return Category.objects.create(name="Макияж")


@pytest.fixture
def group(category):
    return GroupProduct.objects.create(name="Тушь для ресниц", category=category)


@pytest.fixture
def brand(db):
    return Brand.objects.create(name="Some'Brand")


@pytest.fixture
def product(group, brand):
    return Product.objects.create(
        name="Гипоаллергенная тушь для объема",
        group=group,
        brand=brand,
        price=100.50,
        description="Test",
        stock=5,
    )
