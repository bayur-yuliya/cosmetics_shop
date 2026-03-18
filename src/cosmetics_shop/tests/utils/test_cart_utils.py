from unittest.mock import Mock

import pytest
from django.contrib.sessions.middleware import SessionMiddleware

from cosmetics_shop.models import Cart
from cosmetics_shop.utils.cart_utils import get_cart, get_or_create_cart


@pytest.mark.django_db
class TestCartUtils:
    def test_get_cart_authenticated(self, rf, admin_user):
        cart = Cart.objects.create(user=admin_user)

        request = rf.get("/")
        request.user = admin_user

        result = get_cart(request)
        assert result == cart
        assert result.user == admin_user

    def test_get_cart_anonymous_with_session(self, rf, cart):
        session_id = "12345678"
        cart = Cart.objects.create(session_key=session_id)

        request = rf.get("/")
        request.user = type("AnonymousUser", (), {"is_authenticated": False})

        request.session = Mock()
        request.session.session_key = session_id

        assert get_cart(request) == cart

    def test_get_or_create_cart_new_session(self, rf):
        request = rf.get("/")
        request.user = type("AnonymousUser", (), {"is_authenticated": False})

        SessionMiddleware(lambda r: None).process_request(request)

        cart = get_or_create_cart(request)

        assert isinstance(cart, Cart)
        assert cart.session_key == request.session.session_key
        assert Cart.objects.count() == 1
