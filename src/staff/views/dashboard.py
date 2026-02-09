import datetime
from django.contrib.auth.decorators import permission_required
from django.db.models import Count
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.utils import timezone
from cosmetics_shop.models import Favorite
from staff.services.dashboard_service import (
    number_of_completed_orders_today,
    number_of_orders_per_month,
    summ_bill,
    average_bill,
)


@permission_required("staff.dashboard_view", raise_exception=False)
def index(request: HttpRequest) -> HttpResponse:
    today = datetime.date.today()
    completed_orders_today = number_of_completed_orders_today()
    orders_per_month = number_of_orders_per_month(today)
    summ = summ_bill(today)
    average = "{:10.2f}".format(average_bill(today) / 100)
    max_favorite = (
        Favorite.objects.annotate(num_product=Count("product")).order_by("num_product")
    )[0:3]

    current_year = timezone.now().year
    years = range(current_year - 5, current_year + 1)

    return render(
        request,
        "staff/dashboard.html",
        {
            "title": "Главная страница",
            "number_of_completed_orders_today": completed_orders_today,
            "number_of_orders_per_month": orders_per_month,
            "summ_bill": summ,
            "average_bill": average,
            "max_favorite": max_favorite,
            "years": years,
            "current_year": current_year,
        },
    )
