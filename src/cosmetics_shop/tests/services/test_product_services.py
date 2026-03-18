import pytest

from cosmetics_shop.models import Favorite
from cosmetics_shop.services.product_service import (
    change_stock_product,
    favorites_products,
)


@pytest.mark.django_db
def test_change_stock_product(product):
    product_stock = product.stock
    change_stock_product(product.code, 3)
    product.refresh_from_db()
    new_product_stock = product.stock

    assert product_stock == new_product_stock + 3


@pytest.mark.django_db
def test_change_stock_product_more_than_there_is(product):
    with pytest.raises(ValueError, match="Товара недостаточно на складе"):
        change_stock_product(product.code, product.stock + 1)


@pytest.mark.django_db
def test_favorites_products(user, products):
    for product in products:
        Favorite.objects.create(product=product, user=user)
    favorite_products = favorites_products(user)

    assert set(products) == set(favorite_products)
