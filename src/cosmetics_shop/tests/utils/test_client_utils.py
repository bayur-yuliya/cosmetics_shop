import pytest
from django.contrib.sessions.middleware import SessionMiddleware

from cosmetics_shop.utils.client_utils import process_delivery_data


@pytest.mark.django_db
def test_process_delivery_data_anonymous_success(rf):
    post_data = {
        "first_name": "Test first name",
        "last_name": "Test last name",
        "email": "test_email@example.com",
        "phone": "0970000000",
        "city": "Test City",
        "post_office": "Test post office",
    }

    request = rf.post("/delivery/", data=post_data)
    request.user = type("AnonymousUser", (), {"is_authenticated": False})

    SessionMiddleware(lambda r: None).process_request(request)

    address = process_delivery_data(request)

    assert address is not None
    assert address.client.first_name == "Test first name"
    assert address.client.deletion_scheduled_date is not None
    assert request.session["client_data"]["first_name"] == "Test first name"
