import pytest
from django.urls import reverse
from rest_framework import status

from cosmetics_shop.models import Favorite


@pytest.mark.django_db
def test_favorite_duplicate(user, product, api_client):
    Favorite.objects.create(user=user, product=product)

    api_client.force_authenticate(user=user)
    url = reverse("favorite-list")
    data = {"product_id": product.id}

    response = api_client.post(url, data)

    assert response.status_code == status.HTTP_400_BAD_REQUEST

    assert "non_field_errors" in response.data
