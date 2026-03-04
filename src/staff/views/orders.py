from django.contrib import messages
from django.contrib.auth.decorators import permission_required

from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404

from cosmetics_shop.models import (
    Order,
    OrderStatusLog,
    OrderItem,
)
from staff.forms import OrderStatusUpdateForm, OrderFilterForm
from staff.services.order_service import (
    get_latest_order_statuses,
    filter_orders_status,
)
from utils.custom_types import AuthenticatedRequest
from utils.helper_function import get_paginator_page


@permission_required("cosmetics_shop.view_order", raise_exception=True)
def orders(request: HttpRequest) -> HttpResponse:
    latest_statuses = get_latest_order_statuses()

    form = OrderFilterForm(request.GET)
    if form.is_valid():
        latest_statuses = filter_orders_status(latest_statuses, form.cleaned_data)

    page = get_paginator_page(request, latest_statuses)

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

    order = get_object_or_404(Order, code=order_code)
    order_items = OrderItem.objects.filter(order=order).select_related("product")

    if request.method == "POST":
        form = OrderStatusUpdateForm(request.POST, user=request.user, order=order)
        if form.is_valid():
            form.save()
            messages.success(request, "Статус успешно изменен")
            return redirect("order_info", order_code=order.code)
    else:
        form = OrderStatusUpdateForm(user=request.user, order=order)
    order_status_log: QuerySet[OrderStatusLog] = (
        OrderStatusLog.objects.filter(order=order)
        .select_related("changed_by")
        .order_by("-changed_at")
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
