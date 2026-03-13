from unittest.mock import patch

import pytest
from django.contrib.auth.models import Group
from django.utils import timezone

from accounts.models import ActivationToken
from accounts.utils.account_services import (
    send_activation_email,
    activate_user,
    has_active_orders,
    anonymize_client,
    delete_client,
)
from config.settings import DEFAULT_STAFF_GROUP_NAME
from cosmetics_shop.models import Status, DeliveryAddress, Order


@patch("accounts.utils.account_services.send_mail")
def test_send_activation_email(mock_send_mail, user, token):

    send_activation_email(user, token)

    mock_send_mail.assert_called_once()


@pytest.mark.django_db
def test_activate_user_service(user, token):
    group = Group.objects.create(name=DEFAULT_STAFF_GROUP_NAME)
    active_user = activate_user(token=token.token, password="12345678")

    user.refresh_from_db()

    assert active_user == user
    assert user.is_active
    assert user.is_staff
    assert user.check_password("12345678")

    assert group in user.groups.all()
    assert not ActivationToken.objects.filter(token=token.token).exists()


@pytest.mark.django_db
def test_has_active_orders(client):
    Order.objects.create(client=client)
    assert has_active_orders(client) is True


def test_has_no_active_orders(client):
    assert has_active_orders(client) is False


@pytest.mark.django_db
def test_anonymize_client(client, address):
    address.client = client
    address.save()

    anonymize_client(client)

    client.refresh_from_db()

    assert client.first_name == "Аноним"
    assert client.phone == ""
    assert client.is_active is False

    assert not DeliveryAddress.objects.filter(client=client).exists()


@pytest.mark.django_db
def test_delete_client_with_active_orders(client):
    Order.objects.create(client=client)
    delete_client(client)
    client.refresh_from_db()

    assert client.is_pending_deletion is True


@pytest.mark.django_db
def test_delete_client_after_return_period(client):
    order = Order.objects.create(client=client)
    order.client = client
    order.status = Status.COMPLETED
    order.completed_at = timezone.now() - timezone.timedelta(days=20)
    order.save()

    delete_client(client)

    client.refresh_from_db()

    assert client.first_name == "Аноним"
