import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_product_list(product, api_client):
    url = reverse("products-list")
    response = api_client.get(url)

    assert response.status_code == 200
    assert len(response.data) > 0


@pytest.mark.django_db
def test_product_detail(product, api_client):
    url = reverse("products-detail", kwargs={"pk": product.id})
    response = api_client.get(url)

    assert response.status_code == 200
    assert response.data["id"] == product.id


@pytest.mark.django_db
def test_product_soft_delete(admin_client, product):
    url = reverse("products-soft-delete", kwargs={"pk": product.id})
    response = admin_client.post(url)

    assert response.status_code == 200
    product.refresh_from_db()
    assert not product.is_active
