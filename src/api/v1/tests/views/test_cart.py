import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_cart_add(product, api_client):
    url = reverse("cart-add")
    data = {"product_code": product.code}
    response = api_client.post(url, data)

    assert response.status_code == 200
    assert response.data["status"] == "added"


@pytest.mark.django_db
def test_cart_list_empty(api_client):
    url = reverse("cart-list")
    response = api_client.get(url)

    assert response.status_code == 200
    assert response.data["items"] == []
    assert response.data["total_price"] == 0
