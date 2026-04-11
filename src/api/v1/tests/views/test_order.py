import pytest
from django.urls import reverse
from rest_framework import status


@pytest.mark.django_db
def test_order_create_no_cart(api_client):
    url = reverse("orders-list")
    data = {
        "payment_method": "cash",
        "client_data": {
            "first_name": "Test_first_name",
            "last_name": "Test_last_name",
            "phone": "0974539274",
            "email": "test@example.com",
        },
        "address_data": {"city": "City", "post_office": "11"},
    }
    response = api_client.post(url, data, format="json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data["detail"] == "Корзина не найдена"


@pytest.mark.django_db
def test_order_create_empty_cart(cart, api_client, client_obj):
    cart.client = client_obj
    cart.save()

    api_client.force_authenticate(user=client_obj.user)

    url = reverse("orders-list")
    data = {
        "payment_method": "cash",
        "client_data": {
            "first_name": "Test_first_name",
            "last_name": "Test_last_name",
            "phone": "0974539274",
            "email": "test@example.com",
        },
        "address_data": {"city": "City", "post_office": "11"},
    }
    response = api_client.post(url, data, format="json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data["detail"] == "Корзина пуста"


@pytest.mark.django_db
def test_create_order_cash_success(api_client, cart_with_one_item, client_obj, mocker):
    mock_clear = mocker.patch("api.v1.views.orders.clear_cart_after_order")
    mock_create_service = mocker.patch("api.v1.views.orders.create_order_from_cart")

    mock_order = mock_create_service.return_value
    mock_order.id = 123
    mock_order.total_price = 1000
    mock_order.get_status_display.return_value = "Новый"

    api_client.force_authenticate(user=client_obj.user)
    data = {
        "payment_method": "cash",
        "client_data": {
            "first_name": "Test_first_name",
            "last_name": "Test_last_name",
            "phone": "0974539274",
            "email": "test@example.com",
        },
        "address_data": {"city": "City", "post_office": "11"},
    }

    url = reverse("orders-list")
    response = api_client.post(url, data, format="json")

    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["order_id"] == 123
    assert response.data["payment_method"] == "cash"

    # Check that the recycle bin has been emptied
    mock_clear.assert_called_once_with(cart_with_one_item)
