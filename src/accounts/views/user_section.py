from allauth.account.views import logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import HttpResponse
from django.shortcuts import render, redirect

from accounts.forms import ClientCreationForm
from accounts.utils.account_services import delete_client

from cosmetics_shop.models import Client
from cosmetics_shop.services.order_service import get_order_items_by_client
from utils.custom_types import AuthenticatedRequest
from utils.helper_function import get_paginator_page


@login_required
def delete_account(request: AuthenticatedRequest) -> HttpResponse:
    try:
        client = Client.objects.get(user=request.user)
    except Client.DoesNotExist:
        return redirect("main_page")

    with transaction.atomic():
        delete_client(client)
        if not client.is_pending_deletion:
            logout(request)
        else:
            messages.warning(
                request,
                """
                У вас остались незавершенные заказы.
                Аккаунт будет удален после из завершения и 14 дней требующих для возврата.
                Если все равно удалить, свяжитесь с менеджером для отмены заказа.
                """,
            )
    return redirect("main_page")


@login_required
def user_contact(request: AuthenticatedRequest) -> HttpResponse:
    client, created = Client.objects.get_or_create(user=request.user)

    if request.method == "POST":
        form = ClientCreationForm(
            request.POST, instance=client, initial={"email": request.user.email}
        )
        if form.is_valid():
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
    order_items_data = get_order_items_by_client(client)
    page = get_paginator_page(request, order_items_data)

    return render(
        request,
        "accounts/order_history.html",
        {
            "title": "История заказов",
            "order_items": page,
        },
    )
