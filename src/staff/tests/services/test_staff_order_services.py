import pytest
from django.utils.timezone import localtime

from cosmetics_shop.models import Order, OrderStatusLog
from staff.services.order_service import (
    change_order_status_log,
    filter_orders_status,
    get_latest_order_statuses,
)


@pytest.mark.django_db
def test_get_latest_order_statuses(client_obj):
    order1 = Order.objects.create(client=client_obj)
    order2 = Order.objects.create(client=client_obj)

    OrderStatusLog.objects.create(order=order1, status=1)
    last1 = OrderStatusLog.objects.create(order=order1, status=2)

    OrderStatusLog.objects.create(order=order2, status=1)
    last2 = OrderStatusLog.objects.create(order=order2, status=3)

    qs = get_latest_order_statuses()

    assert qs.count() == 2
    assert last1 in qs
    assert last2 in qs


@pytest.mark.django_db
def test_filter_orders_status(client_obj):
    order1 = Order.objects.create(client=client_obj)
    order2 = Order.objects.create(client=client_obj)

    OrderStatusLog.objects.create(order=order1, status=1)
    OrderStatusLog.objects.create(order=order2, status=2)

    qs = OrderStatusLog.objects.all()

    filtered = filter_orders_status(qs, {"status": 1})

    assert filtered.exists()


@pytest.mark.django_db
def test_filter_orders_status_by_date(client_obj):
    order = Order.objects.create(client=client_obj)
    qs = Order.objects.all()
    local_date = localtime(order.created_at).date()

    filtered = filter_orders_status(
        qs,
        {
            "date_from": local_date,
            "date_to": local_date,
        },
    )
    assert filtered.exists()


@pytest.mark.django_db
def test_change_order_status_log_creates_log(client_obj, admin_user):
    order = Order.objects.create(client=client_obj)

    result = change_order_status_log(
        order=order,
        user=admin_user,
        status=2,
        comment="updated",
    )

    assert result is True

    log = OrderStatusLog.objects.filter(order=order).first()

    assert log.status == 2
    assert log.comment == "updated"


@pytest.mark.django_db
def test_change_order_status_log_no_changes(client_obj, admin_user):
    order = Order.objects.create(client=client_obj)

    OrderStatusLog.objects.create(
        order=order,
        status=1,
        comment="same",
    )

    result = change_order_status_log(
        order=order,
        user=admin_user,
        status=1,
        comment="same",
    )

    assert result is False
