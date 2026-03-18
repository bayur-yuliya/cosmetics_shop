import pytest
from django.contrib.auth.models import Group

from cosmetics_shop.tests.conftest import (  # noqa
    brand,
    category,
    category2,
    client_obj,
    group,
    group2,
    products,
    user,
)


@pytest.fixture
def group_permissions():
    return Group.objects.create(name="Test Group of permissions")
