from unittest.mock import Mock

import pytest
from django.test import RequestFactory

from cosmetics_shop.context_processors import (
    cart_item_count,
    is_pending_deletion_client,
    register_form,
)
from cosmetics_shop.tests.conftest import add_session


@pytest.mark.django_db
def test_cart_item_count_empty():
    request = RequestFactory().get("/")
    add_session(request)

    request.user = Mock()
    request.user.is_authenticated = False

    result = cart_item_count(request)

    assert "cart_item_count" in result


@pytest.mark.django_db
def test_register_form():
    request = RequestFactory().get("/")

    result = register_form(request)

    assert "form_register" in result


@pytest.mark.django_db
def test_pending_deletion_anonymous():
    request = RequestFactory().get("/")
    request.user = Mock()
    request.user.is_authenticated = False

    result = is_pending_deletion_client(request)

    assert result["is_pending_deletion"] is None
