from django.contrib import messages
from django.contrib.auth.decorators import permission_required

from django.core.paginator import Paginator
from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404

from cosmetics_shop.models import (
    Order,
    OrderItem,
    OrderStatusLog,
)
from staff.forms import OrderStatusForm
from staff.services.orders_service import (
    get_latest_order_statuses,
    filter_orders_status,
    change_order_status,
)
from utils.custom_types import AuthenticatedRequest


@permission_required("cosmetics_shop.view_order", raise_exception=True)
def orders(request: HttpRequest) -> HttpResponse:
    latest_statuses = get_latest_order_statuses()

    if request.method == "POST":
        form = OrderStatusForm(request.POST)
        if form.is_valid():
            latest_statuses = filter_orders_status(latest_statuses, form.cleaned_data)

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
            status = form.cleaned_data["status"]
            comment = form.cleaned_data["comment"]

            if change_order_status(order, request.user, status, comment):
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
