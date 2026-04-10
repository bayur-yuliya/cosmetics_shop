import pytest
from rest_framework.test import APIClient


@pytest.mark.django_db
def test_cart_add(product):
    client = APIClient()

    response = client.post("/api/v1/cart/add/", {"product_code": product.code})

    assert response.status_code == 200
    assert response.data["status"] == "added"


@pytest.mark.django_db
def test_cart_list_empty():
    client = APIClient()

    response = client.get("/api/v1/cart/")

    assert response.status_code == 200
    assert response.data["items"] == []
    assert response.data["total_price"] == 0
