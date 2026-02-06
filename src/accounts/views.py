from typing import Any

from allauth.account.models import EmailAddress
from allauth.socialaccount.models import SocialAccount
from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import QuerySet, Prefetch
from django.http import HttpResponse, HttpRequest
from django.shortcuts import render, redirect

from accounts.forms import (
    ClientCreationForm,
    SetInitialPasswordForm,
)
from accounts.utils.account_services import (
    activate_user_service,
    login_authenticated_user,
)
from cosmetics_shop.models import Client, Favorite, Order, OrderItem, OrderStatusLog
from utils.custom_types import AuthenticatedRequest


@login_required
def logout_view(request: HttpRequest) -> HttpResponse:
    logout(request)
    return redirect("main_page")


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
def favorites(request: AuthenticatedRequest) -> HttpResponse:
    products = Favorite.objects.filter(user=request.user)

    paginator = Paginator(products, 20)
    page_number = request.GET.get("page")
    page = paginator.get_page(page_number)

    return render(
        request,
        "accounts/favorites.html",
        {
            "title": "Избранное",
            "products": page,
            "is_favorite": True,
        },
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


def activate_account(request: HttpRequest) -> HttpResponse:
    token_value: str | None = request.GET.get("token")
    if token_value is not None:
        if request.method == "POST":
            form = SetInitialPasswordForm(request.POST)
            if form.is_valid():
                password = form.cleaned_data["password1"]
                user = activate_user_service(request, token_value, password)
                login_authenticated_user(request, user, password)
    else:
        messages.error(request, "Не удалось получить токен")
    form = SetInitialPasswordForm()
    return render(
        request,
        "accounts/activate_staff_password.html",
        {
            "title": "Активация приглашения",
            "form": form,
        },
    )


@login_required
def remove_from_favorites(
    request: AuthenticatedRequest, product_id: int
) -> HttpResponse:
    Favorite.objects.filter(user=request.user, product_id=product_id).delete()
    return redirect("favorites")
