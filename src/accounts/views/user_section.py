from typing import Any

from allauth.account.models import EmailAddress
from allauth.socialaccount.models import SocialAccount
from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Prefetch
from django.http import HttpResponse
from django.shortcuts import render, redirect

from accounts.forms import ClientCreationForm

from cosmetics_shop.models import Client, Order, OrderStatusLog
from utils.custom_types import AuthenticatedRequest


@login_required
@transaction.atomic
def delete_account(request: AuthenticatedRequest) -> HttpResponse:
    user = request.user

    SocialAccount.objects.filter(user=user).delete()
    EmailAddress.objects.filter(user=user).delete()

    user.email = None

    user.is_active = False
    user.save()
    user.set_unusable_password()

    logout(request)
    cache.clear()
    return redirect("main_page")


@login_required
def user_contact(request: AuthenticatedRequest) -> HttpResponse:
    client, created = Client.objects.get_or_create(user=request.user)

    if request.method == "POST":
        form = ClientCreationForm(
            request.POST, instance=client, initial={"email": request.user.email}
        )
        if form.is_valid():
            if form.has_changed():
                form.save()
                messages.success(request, "Данные успешно обновлены")
            else:
                messages.info(request, "Изменений не обнаружено")

            return redirect("user_contact")
    form = ClientCreationForm(instance=client, initial={"email": request.user.email})
    return render(
        request,
        "accounts/user_contact.html",
        {"title": "Контактная информация", "form": form, "client": client},
    )


@login_required
def order_history(request: AuthenticatedRequest) -> HttpResponse:
    client, _ = Client.objects.get_or_create(user=request.user)
    status_prefetch = Prefetch(
        "status_log",
        queryset=OrderStatusLog.objects.order_by("-changed_at"),
        to_attr="order_statuses",
    )

    orders = (
        Order.objects.filter(client=client)
        .prefetch_related("items__product", status_prefetch)
        .order_by("-created_at")
    )

    order_items_data: list[dict[str, Any]] = []

    for order in orders:
        latest_status: OrderStatusLog | None = (
            order.order_statuses[0] if order.order_statuses else None
        )

        order_items_data.append(
            {
                "order": order,
                "items": order.items.all(),
                "latest_status": latest_status,
                "status_badge_class": (
                    latest_status.status_badge_class() if latest_status else "secondary"
                ),
            }
        )

    paginator = Paginator(order_items_data, 20)
    page_number = request.GET.get("page")
    page = paginator.get_page(page_number)

    return render(
        request,
        "accounts/order_history.html",
        {
            "title": "История заказов",
            "order_items": page,
        },
    )
