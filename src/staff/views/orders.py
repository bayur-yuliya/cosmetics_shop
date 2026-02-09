from django.contrib import messages
from django.contrib.auth.decorators import permission_required

from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import OuterRef, Subquery, QuerySet
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404

from cosmetics_shop.models import (
    Order,
    OrderItem,
    OrderStatusLog,
)
from staff.forms import OrderStatusForm
from utils.custom_types import AuthenticatedRequest


@permission_required("cosmetics_shop.view_order", raise_exception=True)
def orders(request: HttpRequest) -> HttpResponse:
    latest_status_subquery = OrderStatusLog.objects.filter(
        order=OuterRef("order")
    ).order_by("-changed_at")

    latest_statuses = OrderStatusLog.objects.filter(
        id__in=Subquery(latest_status_subquery.values("id")[:1])
    ).order_by("status")

    if request.method == "POST":
        form = OrderStatusForm(request.POST)
        if form.is_valid():
            status = form.cleaned_data.get("status")
            date_from = form.cleaned_data.get("date_from")
            date_to = form.cleaned_data.get("date_to")
            if status:
                latest_statuses = latest_statuses.filter(status=status)

            if date_from:
                latest_statuses = latest_statuses.filter(
                    order__created_at__gte=date_from
                )
            if date_to:
                latest_statuses = latest_statuses.filter(order__created_at__lte=date_to)

            return render(
                request,
                "staff/orders.html",
                {
                    "title": "Список заказов",
                    "form": form,
                    "status": latest_statuses,
                },
            )
    else:
        form = OrderStatusForm()

    paginator = Paginator(latest_statuses, 20)
    page_number = request.GET.get("page")
    page = paginator.get_page(page_number)

    return render(
        request,
        "staff/orders.html",
        {
            "title": "Список заказов",
            "form": form,
            "status": page,
        },
    )


@permission_required("cosmetics_shop.view_order", raise_exception=True)
def order_info(request: AuthenticatedRequest, order_code: int) -> HttpResponse:
    title = f"Заказ {order_code}"

    order: Order = get_object_or_404(Order, code=order_code)
    order_items: QuerySet[OrderItem] = OrderItem.objects.filter(order=order)

    if request.method == "POST":
        form = OrderStatusForm(request.POST, instance=order, user=request.user)
        if form.is_valid():
            last: OrderStatusLog | None = OrderStatusLog.objects.filter(
                order=order
            ).first()

            if last and (
                last.status != form.cleaned_data["status"]
                or last.comment != form.cleaned_data["comment"]
            ):
                with transaction.atomic():
                    OrderStatusLog.objects.create(
                        order=order,
                        changed_by=request.user,
                        status=form.cleaned_data["status"],
                        comment=form.cleaned_data["comment"],
                    )
                    form.save()
                    messages.success(request, "Статус успешно изменен")
            else:
                messages.success(request, "Статус не изменен")

            return redirect("order_info", order_code=order.code)

    form = OrderStatusForm(instance=order, user=request.user)
    order_status_log: QuerySet[OrderStatusLog] = OrderStatusLog.objects.filter(
        order=order
    )

    return render(
        request,
        "staff/order_info.html",
        {
            "title": title,
            "order": order,
            "order_items": order_items,
            "form": form,
            "order_status_log": order_status_log,
        },
    )
