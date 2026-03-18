from unittest.mock import patch

import pytest
from django.urls import reverse

from cosmetics_shop.models import Favorite, Product


@pytest.mark.django_db
def test_toggle_favorite_remove(client, user, product):
    Favorite.objects.create(user=user, product=product)

    client.force_login(user)

    response = client.post(
        reverse("ajax_toggle_favorites"),
        {"product_id": product.id},
    )

    data = response.json()

    assert data["in_favorites"] is False
    assert not Favorite.objects.filter(user=user, product=product).exists()


@pytest.mark.django_db
def test_toggle_favorite_unauthenticated(client, product):
    response = client.post(
        reverse("ajax_toggle_favorites"),
        {"product_id": product.id},
    )

    data = response.json()

    assert data["in_favorites"] is False
    assert data["message"]["level"] == "warning"


@pytest.mark.django_db
def test_add_to_cart_no_product_code(client):
    response = client.post(reverse("ajax_add_to_cart"))

    assert response.status_code == 400
    assert response.json()["success"] is False


@pytest.mark.django_db
@patch("cosmetics_shop.ajax.add_product_to_cart")
def test_add_to_cart_product_not_found(mock_add, client, product):
    mock_add.side_effect = Product.DoesNotExist

    response = client.post(
        reverse("ajax_add_to_cart"),
        {"product_code": 999},
    )

    assert response.status_code == 404


@pytest.mark.django_db
def test_cart_remove_no_code(client):
    response = client.post(reverse("ajax_cart_remove"))

    assert response.status_code == 400


@pytest.mark.django_db
@patch("cosmetics_shop.ajax.remove_product_from_cart")
def test_cart_remove_error(mock_remove, client):
    mock_remove.side_effect = Exception("test error")

    response = client.post(
        reverse("ajax_cart_remove"),
        {"product_code": 123},
    )

    assert response.status_code == 500
    assert response.json()["success"] is False
