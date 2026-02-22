from django.db import transaction
from django.db.models import QuerySet, OuterRef, Subquery

from cosmetics_shop.models import OrderStatusLog, Order


def get_latest_order_statuses() -> QuerySet[OrderStatusLog]:
    latest_status_ids = (
        OrderStatusLog.objects.filter(order=OuterRef("order"))
        .order_by("-changed_at")
        .values("id")[:1]
    )
    return OrderStatusLog.objects.filter(id__in=Subquery(latest_status_ids))


def filter_orders_status(queryset: QuerySet, filters: dict) -> QuerySet:
    if filters.get("status"):
        queryset = queryset.filter(status=filters["status"])
    if filters.get("date_from"):
        queryset = queryset.filter(order__created_at__gte=filters["date_from"])
    if filters.get("date_to"):
        queryset = queryset.filter(order__created_at__lte=filters["date_to"])
    return queryset.order_by("status")


def change_order_status(order: Order, user, status: str, comment: str) -> bool:
    last_log = OrderStatusLog.objects.filter(order=order).first()

    if last_log and last_log.status == status and last_log.comment == comment:
        return False

    with transaction.atomic():
        OrderStatusLog.objects.create(
            order=order,
            changed_by=user,
            status=status,
            comment=comment,
        )
    return True
