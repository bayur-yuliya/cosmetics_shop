import logging

from allauth.account.views import logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from accounts.forms import ClientCreationForm
from accounts.utils.account_services import delete_client
from cosmetics_shop.models import Client
from cosmetics_shop.services.order_service import get_order_items_by_client
from utils.custom_types import AuthenticatedRequest
from utils.helper_function import get_paginator_page

logger = logging.getLogger(__name__)


@login_required
def delete_account(request: AuthenticatedRequest) -> HttpResponse:
    logger.info(f"Delete account request: user_id={request.user.id}")

    try:
        client = Client.objects.get(user=request.user)
    except Client.DoesNotExist:
        logger.warning(f"Client not found for user: user_id={request.user.id}")
        return redirect("main_page")

    with transaction.atomic():
        delete_client(client)
        if not client.is_pending_deletion:
            logger.info(f"Account fully deleted: user_id={request.user.id}")
            logout(request)
            messages.success(request, "Аккаунт успешно удален!")
        else:
            logger.info(f"Account marked for deletion: user_id={request.user.id}")
            messages.warning(
                request,
                """
                У вас остались незавершенные заказы.
                Аккаунт будет удален после из завершения 
                и 14 дней, требующихся для возврата.
                Если все равно удалить, свяжитесь с менеджером для отмены заказа.
                """,
            )
            return redirect("user_contact")
    return redirect("main_page")


@login_required
def reset_account_deletion(request: AuthenticatedRequest) -> HttpResponse:
    logger.info(f"Reset deletion request: user_id={request.user.id}")

    client = get_object_or_404(Client, user=request.user)
    with transaction.atomic():
        client.is_pending_deletion = False
        client.deletion_scheduled_date = None
        client.save()

    logger.info(f"Deletion reset: client_id={client.id}")

    return redirect("user_contact")


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
