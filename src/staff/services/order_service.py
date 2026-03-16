from datetime import datetime, time

from django.db import transaction
from django.db.models import QuerySet, OuterRef, Subquery
from django.utils import timezone

from cosmetics_shop.models import OrderStatusLog, Order
from utils.date_utils import to_date


def get_latest_order_statuses() -> QuerySet[OrderStatusLog]:
    latest_status_ids = (
        OrderStatusLog.objects.filter(order=OuterRef("order"))
        .order_by("-changed_at", "-id")
        .values("id")[:1]
    )
    return OrderStatusLog.objects.filter(
        id__in=Subquery(latest_status_ids)
    ).select_related("order")


def filter_orders_status(queryset: QuerySet, filters: dict) -> QuerySet:
    orm_filters = {}

    if filters.get("status"):
        orm_filters["status"] = filters["status"]

    if filters.get("date_from"):
        date_from = to_date(filters["date_from"])
        orm_filters["created_at__gte"] = timezone.make_aware(
            datetime.combine(date_from, time.min)
        )

    if filters.get("date_to"):
        date_to = to_date(filters["date_to"])
        orm_filters["created_at__lte"] = timezone.make_aware(
            datetime.combine(date_to, time.max)
        )

    return queryset.filter(**orm_filters).order_by("status")


def change_order_status_log(order: Order, user, status: int, comment: str) -> bool:
    last_log = OrderStatusLog.objects.filter(order=order).first()

    if last_log and last_log.status == status and last_log.comment == comment:
        return False
    with transaction.atomic():
        order.status = status
        order.save()
        order.set_status(status, user=user, comment=comment)
    return True
