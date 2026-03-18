from datetime import timedelta
from decimal import Decimal

import pytest
from django.utils import timezone

from accounts.models import CustomUser
from cosmetics_shop.models import Favorite, Order, Status
from staff.services.dashboard_service import (
    get_completed_orders_queryset,
    get_dashboard_context,
    get_month_stats,
    get_today_stats,
)


@pytest.mark.django_db
def test_get_completed_orders_queryset(client_obj):
    date = timezone.now()
    old_date = date - timedelta(weeks=5)

    Order.objects.create(client=client_obj, status=Status.NEW, completed_at=date)
    Order.objects.create(client=client_obj, status=Status.COMPLETED, completed_at=date)
    Order.objects.create(
        client=client_obj, status=Status.COMPLETED, completed_at=old_date
    )

    orders = get_completed_orders_queryset(date)

    count_completed_orders_at_month = Order.objects.filter(
        status=Status.COMPLETED, completed_at=date
    ).count()

    assert orders.count() == count_completed_orders_at_month
    assert orders[0].status == Status.COMPLETED
    assert orders[0].completed_at == date


@pytest.mark.django_db
def test_get_today_stats(client_obj):
    date = timezone.now()
    yesterday = date - timedelta(days=1)
    old_date = date - timedelta(weeks=5)

    Order.objects.create(client=client_obj, status=Status.NEW, completed_at=date)
    Order.objects.create(client=client_obj, status=Status.COMPLETED, completed_at=date)
    Order.objects.create(
        client=client_obj, status=Status.COMPLETED, completed_at=yesterday
    )
    Order.objects.create(
        client=client_obj, status=Status.COMPLETED, completed_at=old_date
    )

    orders = get_today_stats()

    count_completed_orders_today = Order.objects.filter(
        status=Status.COMPLETED, completed_at=date
    ).count()

    assert orders["total_orders"] == count_completed_orders_today


@pytest.mark.django_db
def test_get_month_stats(client_obj):
    date = timezone.now()
    yesterday = date - timedelta(days=1)
    old_date = date - timedelta(weeks=5)

    Order.objects.create(
        client=client_obj, status=Status.NEW, completed_at=date, total_price=650.50
    )
    Order.objects.create(
        client=client_obj, status=Status.COMPLETED, completed_at=date, total_price=1200
    )
    Order.objects.create(
        client=client_obj,
        status=Status.COMPLETED,
        completed_at=yesterday,
        total_price=500.50,
    )
    Order.objects.create(
        client=client_obj,
        status=Status.COMPLETED,
        completed_at=old_date,
        total_price=230,
    )

    month_stats = get_month_stats(date)

    assert month_stats["total_orders"] == 2
    assert month_stats["total_revenue"] == 1700
    assert month_stats["avg_check"] == Decimal("850.25")


@pytest.mark.django_db
def test_get_dashboard_context_max_favorite(user, client_obj, products):
    for product in products:
        Favorite.objects.create(user=user, product=product)

    new_user = CustomUser.objects.create_user(
        email="test_new_user@test.com", password="12345678"
    )

    expected_products = sorted(products[:3], key=lambda x: x.id)

    for product in expected_products:
        Favorite.objects.create(user=new_user, product=product)

    context = get_dashboard_context()

    result_products = list(context["max_favorite"])

    assert len(result_products) == 3
    for p in expected_products:
        assert p in result_products
