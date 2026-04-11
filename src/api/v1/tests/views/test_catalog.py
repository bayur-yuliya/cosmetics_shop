import pytest


@pytest.mark.django_db
def test_product_list(product, api_client):
    response = api_client.get("/api/v1/catalog/products/")

    assert response.status_code == 200
    assert len(response.data) > 0


@pytest.mark.django_db
def test_product_detail(product, api_client):
    response = api_client.get(f"/api/v1/catalog/products/{product.id}/")

    assert response.status_code == 200
    assert response.data["id"] == product.id


@pytest.mark.django_db
def test_product_soft_delete(admin_client, product):
    response = admin_client.post(f"/api/v1/catalog/products/{product.id}/soft_delete/")

    assert response.status_code == 200
    product.refresh_from_db()
    assert not product.is_active
