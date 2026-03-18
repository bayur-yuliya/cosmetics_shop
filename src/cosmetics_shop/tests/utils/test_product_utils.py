import pytest
from django.contrib.auth.models import AnonymousUser
from django.test import RequestFactory

from cosmetics_shop.utils.product_utils import get_ready_product_list


@pytest.mark.django_db
def test_get_ready_product_list_authenticated(user, products):
    from cosmetics_shop.models import Favorite

    for product in products:
        Favorite.objects.create(product=product, user=user)

    factory = RequestFactory()
    request = factory.get("/")
    request.user = user

    result = get_ready_product_list(request)

    assert set(result) == set(products)


@pytest.mark.django_db
def test_get_ready_product_list_anonymous(products):
    factory = RequestFactory()
    request = factory.get("/")
    request.user = AnonymousUser()

    products[0].is_active = False
    products[0].save()

    result = get_ready_product_list(request)

    expected = [p for p in products if p.is_active]

    assert set(result) == set(expected)
