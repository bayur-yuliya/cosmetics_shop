from dateutil.relativedelta import relativedelta
from django.db.models import Avg, Sum, Count
from django.utils import timezone

from cosmetics_shop.models import Order, Status


def get_completed_orders_queryset(start_date):
    return (
        Order.objects.filter(
            created_at__gte=start_date,
            status=Status.COMPLETED,
        )
        .distinct()
    )


def get_today_stats():
    today = timezone.now().date()

    qs = get_completed_orders_queryset(today)

    return {
        "total_orders": qs.count(),
    }


def get_month_stats(current_date):
    one_month_ago = current_date - relativedelta(months=1)

    qs = get_completed_orders_queryset(one_month_ago)

    stats = qs.aggregate(
        total_orders=Count("id"),
        total_revenue=Sum("total_price"),
        avg_check=Avg("total_price"),
    )

    return {
        "total_orders": stats["total_orders"] or 0,
        "total_revenue": int(stats["total_revenue"] or 0),
        "avg_check": round(stats["avg_check"] or 0, 2),
    }
