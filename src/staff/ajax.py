import logging
from datetime import date

from django.db.models import Avg, Count
from django.db.models.functions import TruncMonth
from django.http import HttpRequest, JsonResponse
from django.utils import timezone

from cosmetics_shop.models import Order, Status

logger = logging.getLogger(__name__)


def sales_comparison_chart_for_the_year(request: HttpRequest) -> JsonResponse:
    year: str | None = request.GET.get("year")
    now = timezone.now()

    logger.debug(f"Sales chart requested: year={year}")

    if year is not None:
        try:
            current_year = date(int(year), 1, 1).year
        except (TypeError, ValueError):
            logger.warning(f"Invalid year provided: {year}")
            current_year = now.year
    else:
        current_year = now.year

    logger.debug(f"Using year: {current_year}")

    orders_by_month = (
        Order.objects.filter(created_at__year=current_year, status=Status.COMPLETED)
        .annotate(month=TruncMonth("created_at"))
        .values("month")
        .annotate(
            count=Count("id"),
            avg_price=Avg("total_price"),
        )
    )

    logger.info(f"Sales data aggregated for year={current_year}")

    sales_counts = [0] * 12
    average_bill_counts = [0] * 12
    for item in orders_by_month:
        month = item["month"].month - 1
        sales_counts[month] = item["count"]
        average_bill_counts[month] = round(item["avg_price"] or 0, 2)

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
