from django.db.models import Count, Avg
from django.db.models.functions import TruncMonth
from django.http import JsonResponse
from django.utils import timezone

from cosmetics_shop.models import Order


def sales_comparison_chart_for_the_year(request):
    year = request.GET.get("year")
    now = timezone.now()

    try:
        year = int(year)

    except (TypeError, ValueError):
        year = now.year

    orders_by_month = (
        Order.objects.filter(created_at__year=year)
        .annotate(month=TruncMonth("created_at"))
        .values("month")
        .annotate(
            count=Count("id"),
            avg_price=Avg("total_price"),
        )
    )
    sales_counts = [0] * 12
    average_bill_counts = [0] * 12
    for item in orders_by_month:
        month = item["month"].month - 1
        sales_counts[month] = item["count"]
        price = item["avg_price"] / 100
        average_bill_counts[month] = round(price or 0, 2)

    return JsonResponse(
        {
            "labels": [
                "Янв",
                "Фев",
                "Мар",
                "Апр",
                "Май",
                "Июн",
                "Июл",
                "Авг",
                "Сен",
                "Окт",
                "Ноя",
                "Дек",
            ],
            "current_year": year,
            "sales": sales_counts,
            "average_bill": average_bill_counts,
        }
    )
