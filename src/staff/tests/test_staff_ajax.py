import json
from datetime import datetime

import pytest
from django.test import RequestFactory
from django.utils import timezone

from cosmetics_shop.models import Order, Status
from staff.ajax import sales_comparison_chart_for_the_year


@pytest.mark.django_db
def test_sales_chart_with_data():
    factory = RequestFactory()
    request = factory.get("/?year=2026")

    dt_january = timezone.make_aware(datetime(2026, 1, 1))
    dt_february = timezone.make_aware(datetime(2026, 2, 1))

    Order.objects.create(status=Status.COMPLETED, total_price=100)
    Order.objects.create(status=Status.COMPLETED, total_price=200)
    Order.objects.create(status=Status.COMPLETED, total_price=300)

    Order.objects.filter(id__lt=3).update(created_at=dt_january)
    Order.objects.filter(id=3).update(created_at=dt_february)

    response = sales_comparison_chart_for_the_year(request)
    data = json.loads(response.content)

    assert data["sales"][0] == 2
    assert data["average_bill"][0] == "150.00"

    assert data["sales"][1] == 1
    assert data["average_bill"][1] == "300.00"

    assert sum(data["sales"][2:]) == 0


@pytest.mark.django_db
def test_sales_chart_empty():
    factory = RequestFactory()
    request = factory.get("/?year=2026")

    response = sales_comparison_chart_for_the_year(request)
    data = json.loads(response.content)

    assert data["sales"] == [0] * 12
    assert data["average_bill"] == [0] * 12


@pytest.mark.django_db
def test_invalid_year_fallback(mocker):
    factory = RequestFactory()

    fixed_now = timezone.now()
    mocker.patch("staff.ajax.timezone.now", return_value=fixed_now)

    request = factory.get("/?year=invalid")

    response = sales_comparison_chart_for_the_year(request)
    data = json.loads(response.content)

    assert data["current_year"] == "invalid"


@pytest.mark.django_db
def test_ignore_non_completed_orders():
    factory = RequestFactory()
    request = factory.get("/?year=2026")

    dt = timezone.make_aware(datetime(2026, 1, 1))

    Order.objects.create(status=Status.IN_PROGRESS, total_price=100)
    Order.objects.all().update(created_at=dt)

    response = sales_comparison_chart_for_the_year(request)
    data = json.loads(response.content)

    assert data["sales"][0] == 0


@pytest.mark.django_db
def test_average_rounding():
    factory = RequestFactory()
    request = factory.get("/?year=2026")

    dt = timezone.make_aware(datetime(2026, 1, 1))

    Order.objects.create(status=Status.COMPLETED, total_price=100)
    Order.objects.create(status=Status.COMPLETED, total_price=101)

    Order.objects.all().update(created_at=dt)

    response = sales_comparison_chart_for_the_year(request)
    data = json.loads(response.content)

    assert data["average_bill"][0] == "100.50"
