import pytest
from rest_framework.test import APIClient

from cosmetics_shop.tests.conftest import (  # noqa
    brand,
    cart,
    cart_with_one_item,
    category,
    client_obj,
    group,
    order_factory,
    other_user,
    product,
    tag,
    user,
)


@pytest.fixture
def api_client():
    client = APIClient()
    return client
