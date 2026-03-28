from datetime import datetime

from django.core.cache import cache
from django.utils import timezone

from cosmetics_shop.models import Order


def to_date(value):
    if isinstance(value, datetime):
        return value.date()
    return value


def get_first_order_year():
    cache_key = "stats:first_order_year"
    first_year = cache.get(cache_key)

    if first_year is None:
        first_order = Order.objects.order_by("created_at").first()
        if first_order:
            first_year = first_order.created_at.year
        else:
            first_year = timezone.now().year

        cache.set(cache_key, first_year, timeout=None)

    return first_year
