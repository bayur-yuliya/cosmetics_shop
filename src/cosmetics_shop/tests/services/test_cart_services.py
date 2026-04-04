import pytest

from cosmetics_shop.models import Cart, CartItem
from cosmetics_shop.services.cart_services import (
    add_product_to_cart,
    clear_cart_after_order,
    delete_cart,
    delete_product_from_cart,
    get_cart_total_price,
    get_id_products_in_cart,
    is_product_in_cart,
    remove_product_from_cart,
)


@pytest.mark.django_db
def test_get_id_products_in_cart(cart, products):
    for product in products:
        CartItem.objects.create(cart=cart, product=product, quantity=1)
    ids2 = get_id_products_in_cart(cart)
    assert ids2 == [1, 2, 3, 4]


@pytest.mark.django_db
def test_add_product_to_cart(cart, product):
    assert CartItem.objects.filter(cart=cart).count() == 0

    add_product_to_cart(cart, product.code)
    assert CartItem.objects.filter(cart=cart).count() == 1

    cart_item = CartItem.objects.get(cart=cart)

    assert cart_item.product == product
    assert cart_item.quantity == 1


@pytest.mark.django_db
def test_remove_product_from_cart(cart, product):
    CartItem.objects.create(cart=cart, product=product, quantity=3)
    remove_product_from_cart(cart, product.code)

    cart_item = CartItem.objects.get(cart=cart)

    assert cart_item.product == product
    assert cart_item.quantity == 2


@pytest.mark.django_db
def test_delete_product_from_cart(cart, product):
    CartItem.objects.create(cart=cart, product=product, quantity=3)
    delete_product_from_cart(cart, product.code)
    cart_item = CartItem.objects.filter(cart=cart, product=product).count()

    assert cart_item == 0


@pytest.mark.django_db
def test_delete_cart(cart, products):
    for product in products:
        CartItem.objects.create(cart=cart, product=product, quantity=1)

    assert CartItem.objects.filter(cart=cart).count() == len(products)

    delete_cart(cart)

    assert CartItem.objects.filter(cart=cart).count() == 0


@pytest.mark.django_db
def test_is_product_in_cart(cart, product):
    assert not is_product_in_cart(cart, product_pk=product.id)

    CartItem.objects.create(cart=cart, product=product)

    assert is_product_in_cart(cart, product_pk=product.id)


@pytest.mark.django_db
def test_get_cart_total_price(cart, products):
    for product in products:
        CartItem.objects.create(cart=cart, product=product, quantity=1)
    cart_items = CartItem.objects.filter(cart=cart)
    total = get_cart_total_price(cart_items)

    assert total == sum(cart_items.values_list("product__price", flat=True))


@pytest.mark.django_db
def test_clear_cart_after_order(user, product):
    cart = Cart.objects.create(user=user)
    CartItem.objects.create(cart=cart, product=product, quantity=2)
    clear_cart_after_order(cart)
    assert not CartItem.objects.filter(cart=cart)
