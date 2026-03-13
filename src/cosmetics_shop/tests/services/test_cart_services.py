import pytest

from cosmetics_shop.models import Cart, CartItem
from cosmetics_shop.services.cart_services import clear_cart_after_order


@pytest.mark.django_db
def test_clear_cart_after_order(user, product):
    cart = Cart.objects.create(user=user)
    CartItem.objects.create(cart=cart, product=product, quantity=2)
    clear_cart_after_order(cart)
    assert not CartItem.objects.filter(cart=cart)
