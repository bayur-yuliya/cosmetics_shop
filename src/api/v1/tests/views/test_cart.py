import pytest


@pytest.mark.django_db
def test_cart_add(product, api_client):
    response = api_client.post("/api/v1/cart/add/", {"product_code": product.code})

    assert response.status_code == 200
    assert response.data["status"] == "added"


@pytest.mark.django_db
def test_cart_list_empty(api_client):
    response = api_client.get("/api/v1/cart/")

    assert response.status_code == 200
    assert response.data["items"] == []
    assert response.data["total_price"] == 0
