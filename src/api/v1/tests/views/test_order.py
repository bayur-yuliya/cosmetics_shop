import pytest
from rest_framework.test import APIClient


@pytest.mark.django_db
def test_order_create_no_cart():
    client = APIClient()

    response = client.post("/api/v1/orders/", {})

    assert response.status_code == 400


@pytest.mark.django_db
def test_order_create_empty_cart(cart):
    client = APIClient()

    response = client.post("/api/v1/orders/", {})

    assert response.status_code == 400
