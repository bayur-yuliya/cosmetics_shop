from unittest.mock import Mock, patch

import pytest
from django.contrib.messages.storage.fallback import FallbackStorage
from django.http import HttpResponse
from django.test import RequestFactory

from cosmetics_shop.models import Order
from cosmetics_shop.utils.decorators import cart_required, order_session_required


@pytest.mark.django_db
@patch("cosmetics_shop.utils.decorators.get_cart")
def test_cart_required_empty_cart(mock_get_cart, user):
    request = RequestFactory().get("/")

    request.session = {}
    request.user = user

    setattr(request, "_messages", FallbackStorage(request))

    cart = Mock()
    cart_items = Mock()
    cart_items.exists.return_value = False

    cart.cart_items.all.return_value = cart_items
    mock_get_cart.return_value = cart

    def test_view(request):
        return HttpResponse("ok")

    wrapped = cart_required(test_view)

    response = wrapped(request)

    assert response.status_code == 302


@pytest.mark.django_db
@patch("cosmetics_shop.utils.decorators.get_cart")
def test_cart_required_with_items(mock_get_cart):
    request = RequestFactory().get("/")

    request.session = {}

    setattr(request, "_messages", FallbackStorage(request))

    cart = Mock()
    cart_items = Mock()
    cart_items.exists.return_value = True

    cart.cart_items.all.return_value = cart_items
    mock_get_cart.return_value = cart

    def test_view(request):
        return HttpResponse("ok")

    wrapped = cart_required(test_view)

    response = wrapped(request)

    assert response.status_code == 200


@pytest.mark.django_db
def test_order_session_required_no_order():
    request = RequestFactory().get("/")

    request.session = {}
    setattr(request, "_messages", FallbackStorage(request))

    def view(request):
        return HttpResponse("ok")

    wrapped = order_session_required(view)

    response = wrapped(request)

    assert response.status_code == 302


@pytest.mark.django_db
def test_order_session_required_success(client_obj):
    request = RequestFactory().get("/")
    order = Order.objects.create(client=client_obj)

    request.session = {"order_id": order.id}
    setattr(request, "_messages", FallbackStorage(request))

    def view(request):
        return HttpResponse("ok")

    wrapped = order_session_required(view)

    response = wrapped(request)

    assert response.status_code == 200
