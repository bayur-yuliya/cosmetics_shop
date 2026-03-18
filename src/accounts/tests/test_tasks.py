from datetime import timedelta

import pytest
from django.utils import timezone

from accounts.tasks import process_client_anonymization, update_pending_deletion_dates
from cosmetics_shop.models import Client, Order, Status


@pytest.mark.django_db
def test_anonymize_client(mocker):
    client = Client.objects.create(
        is_active=True, deletion_scheduled_date=timezone.now()
    )

    mocker.patch("accounts.tasks.has_active_orders", return_value=False)
    mock_anonymize = mocker.patch("accounts.tasks.anonymize_client")

    process_client_anonymization()

    mock_anonymize.assert_called_once_with(client)


@pytest.mark.django_db
def test_client_has_active_orders(mocker):
    client = Client.objects.create(
        is_active=True, is_pending_deletion=True, deletion_scheduled_date=timezone.now()
    )

    mocker.patch("accounts.tasks.has_active_orders", return_value=True)

    process_client_anonymization()

    client.refresh_from_db()

    assert client.deletion_scheduled_date is None
    assert client.is_pending_deletion is False


@pytest.mark.django_db
def test_set_deletion_date_from_last_order(mocker):
    client = Client.objects.create(
        is_pending_deletion=True, deletion_scheduled_date=None
    )

    completed_at = timezone.now()

    Order.objects.create(
        client=client, status=Status.COMPLETED, completed_at=completed_at
    )

    mocker.patch("accounts.tasks.has_active_orders", return_value=False)

    update_pending_deletion_dates()

    client.refresh_from_db()

    assert client.deletion_scheduled_date == completed_at + timedelta(days=14)


@pytest.mark.django_db
def test_no_orders_calls_anonymize(mocker):
    client = Client.objects.create(
        is_pending_deletion=True, deletion_scheduled_date=None
    )

    mocker.patch("accounts.tasks.has_active_orders", return_value=False)
    mock_anonymize = mocker.patch("accounts.tasks.anonymize_client")

    update_pending_deletion_dates()

    mock_anonymize.assert_called_once_with(client)


@pytest.mark.django_db
def test_has_active_orders_skip(mocker):
    client = Client.objects.create(
        is_pending_deletion=True, deletion_scheduled_date=None
    )

    mocker.patch("accounts.tasks.has_active_orders", return_value=True)
    mock_anonymize = mocker.patch("accounts.tasks.anonymize_client")

    update_pending_deletion_dates()

    client.refresh_from_db()

    assert client.deletion_scheduled_date is None
    mock_anonymize.assert_not_called()
