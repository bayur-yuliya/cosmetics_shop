import logging

from dateutil.relativedelta import relativedelta
from django.db.models import Avg, Count, Sum
from django.utils import timezone

from cosmetics_shop.models import Order, Product, Status

logger = logging.getLogger(__name__)


def get_completed_orders_queryset(start_date):
    logger.debug(f"Fetching completed orders from: {start_date}")

    return Order.objects.filter(
        completed_at__gte=start_date,
        status=Status.COMPLETED,
    ).distinct()


def get_today_stats():
    today = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)

    logger.debug(f"Calculating today's stats: date={today}")

    qs = get_completed_orders_queryset(today)
    total = qs.count()

    logger.info(f"Today's stats: total_orders={total}")

    return {
        "total_orders": total,
    }


def get_month_stats(current_date):
    one_month_ago = current_date - relativedelta(months=1)

    logger.debug(f"Calculating month stats from: {one_month_ago}")

    qs = get_completed_orders_queryset(one_month_ago)

    stats = qs.aggregate(
        total_orders=Count("id"),
        total_revenue=Sum("total_price"),
        avg_check=Avg("total_price"),
    )

    logger.info(
        f"Month stats: orders={stats['total_orders']}, "
        f"revenue={stats['total_revenue']}, avg={stats['avg_check']}"
    )

    return {
        "total_orders": stats["total_orders"] or 0,
        "total_revenue": int(stats["total_revenue"] or 0),
        "avg_check": round(stats["avg_check"] or 0, 2),
    }


def get_dashboard_context():
    logger.debug("Building dashboard context")

    today = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)

    today_stats = get_today_stats()
    month_stats = get_month_stats(today)

    max_favorite = (
        Product.objects.annotate(fav_count=Count("favorites"))
        .filter(fav_count__gt=0)
        .order_by("-fav_count")[:3]
    )

    current_year = timezone.now().year
    years = range(current_year - 5, current_year + 1)

    logger.info(
        f"Dashboard loaded: today_orders={today_stats['total_orders']}, "
        f"month_orders={month_stats['total_orders']}"
    )

    return {
        "number_of_completed_orders_today": today_stats["total_orders"],
        "number_of_orders_per_month": month_stats["total_orders"],
        "summ_bill": month_stats["total_revenue"],
        "average_bill": month_stats["avg_check"],
        "max_favorite": max_favorite,
        "years": years,
        "current_year": current_year,
    }
