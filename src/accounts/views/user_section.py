from allauth.account.models import EmailAddress
from allauth.socialaccount.models import SocialAccount
from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.core.paginator import Paginator
from django.db import transaction
from django.http import HttpResponse
from django.shortcuts import render, redirect

from accounts.forms import ClientCreationForm

from cosmetics_shop.models import Client
from cosmetics_shop.services.order_service import get_order_items_by_client
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
    order_items_data = get_order_items_by_client(client)

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
