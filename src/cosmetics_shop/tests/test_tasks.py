from datetime import timedelta
from decimal import Decimal

import pytest
from django.utils import timezone

from cosmetics_shop.models import Payment, Status
from cosmetics_shop.tasks import cleanup_expired_orders


@pytest.mark.django_db
def test_no_expired_orders():
    result = cleanup_expired_orders()

    assert result == "No expired orders found."


@pytest.mark.django_db
def test_paid_order_not_canceled(order_factory):
    last_time = timezone.now() - timedelta(minutes=32)

    order = order_factory(status=Status.NEW)
    order.created_at = last_time
    order.save()

    Payment.objects.create(
        order=order,
        method="card",
        amount=Decimal(100.00),
        external_id="11111",
        status=Payment.PaymentStatus.SUCCESS,
    )

    cleanup_expired_orders()
    order.refresh_from_db()

    assert order.status == Status.NEW


@pytest.mark.django_db
def test_cash_orders_not_expired(order_factory, payment_factory):
    last_time = timezone.now() - timedelta(minutes=32)

    order = order_factory(status=Status.NEW)
    order.created_at = last_time
    order.save()

    payment_factory(
        order=order,
        method=Payment.PaymentMethod.CASH,
        status=Payment.PaymentStatus.PENDING,
    )

    cleanup_expired_orders()

    order.refresh_from_db()

    assert order.status != Status.CANCELED


@pytest.mark.django_db
def test_stock_restored(order_factory, order_item_factory, product, payment_factory):
    start_product_stock = product.stock
    last_time = timezone.now() - timedelta(minutes=60)

    order = order_factory(status=Status.NEW)
    order.created_at = last_time
    order.save()

    order_item_factory(order=order, product=product, quantity=2)

    # we clearly reduce it to simulate the order
    product.stock -= 2
    product.save()

    payment_factory(
        order=order,
        method=Payment.PaymentMethod.CARD,
        status=Payment.PaymentStatus.FAILED,
    )

    cleanup_expired_orders()

    product.refresh_from_db()

    assert product.stock == start_product_stock


@pytest.mark.django_db
def test_pending_payments_marked_failed(order_factory, payment_factory):
    last_time = timezone.now() - timedelta(minutes=60)

    order = order_factory(status=Status.NEW)
    order.created_at = last_time
    order.save()

    payment = payment_factory(
        order=order,
        status=Payment.PaymentStatus.FAILED,
        method=Payment.PaymentMethod.CARD,
    )

    cleanup_expired_orders()

    payment.refresh_from_db()

    assert payment.status == Payment.PaymentStatus.FAILED


@pytest.mark.django_db
def test_error_does_not_crash_task(
    order_factory, order_item_factory, product, payment_factory
):
    last_time = timezone.now() - timedelta(minutes=60)

    order = order_factory(status=Status.NEW)
    order.created_at = last_time
    order.save()

    order_item_factory(order=order, product=product, quantity=1)

    payment_factory(
        order=order,
        status=Payment.PaymentStatus.PENDING,
        method=Payment.PaymentMethod.CARD,
    )

    result = cleanup_expired_orders()

    assert "Successfully expired 1 orders." in result
