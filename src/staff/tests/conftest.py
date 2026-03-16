import pytest
from django.contrib.auth.models import Group

from cosmetics_shop.tests.conftest import (  # noqa
    user,
    client_obj,
    group,
    group2,
    brand,
    products,
    category,
    category2,
)


@pytest.fixture
def group_permissions():
    return Group.objects.create(name="Test Group of permissions")
