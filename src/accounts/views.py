from typing import List, Dict, Optional, cast

from allauth.account.models import EmailAddress
from allauth.account.views import login
from allauth.socialaccount.models import SocialAccount
from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import QuerySet
from django.http import HttpResponse, HttpRequest
from django.shortcuts import render, redirect

from accounts.forms import (
    ClientCreationForm,
    SetInitialPasswordForm,
)
from accounts.models import ActivationToken, CustomUser
from accounts.utils.validators import validate_activation_token
from cosmetics_shop.models import Client, Favorite, Order


@login_required
def logout_view(request: HttpRequest) -> HttpResponse:
    logout(request)
    return redirect("main_page")


@login_required
@transaction.atomic
def delete_account(request: HttpRequest) -> HttpResponse:
    user = cast(CustomUser, request.user)

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
def user_contact(request: HttpRequest) -> HttpResponse:
    user = cast(CustomUser, request.user)
    client, created = Client.objects.get_or_create(user=user)

    if request.method == "POST":
        form = ClientCreationForm(
            request.POST, instance=client, initial={"email": user.email}
        )
        if form.is_valid():
            if form.has_changed():
                form.save()
                messages.success(request, "Данные успешно обновлены")
            else:
                messages.info(request, "Изменений не обнаружено")

            return redirect("user_contact")
    form = ClientCreationForm(instance=client, initial={"email": user.email})
    return render(
        request,
        "accounts/user_contact.html",
        {"title": "Контактная информация", "form": form, "client": client},
    )


@login_required
def favorites(request: HttpRequest) -> HttpResponse:
    user = cast(CustomUser, request.user)
    products = Favorite.objects.filter(user=user)

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
def order_history(request: HttpRequest) -> HttpResponse:
    user = cast(CustomUser, request.user)
    client, _ = Client.objects.get_or_create(user=user)
    orders: QuerySet[Order] = Order.objects.filter(client=client).prefetch_related(
        "items", "status_log"
    )
    order_items: List[Dict] = []

    for order in orders:
        items = list(order.items.all())
        status = order.status_log.first()

        order_items.append(
            {
                "order": order,
                "items": items,
                "status": status,
                "status_badge_class": (status.status_badge_class() if status else None),
            }
        )

    paginator = Paginator(order_items, 20)
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
    token_value: Optional[str] = request.GET.get("token")
    if token_value:
        validate_activation_token(request, token_value)
        token_obj: ActivationToken = ActivationToken.objects.get(token=token_value)

        user: CustomUser = token_obj.user
        if request.method == "POST":
            form = SetInitialPasswordForm(request.POST)
            if form.is_valid():
                password = form.cleaned_data["password1"]

                user.set_password(password)
                user.is_active = True
                user.is_staff = True
                user.save()

                token_obj.delete()
                messages.success(request, "Аккаунт активирован!")

                from django.contrib.auth import authenticate

                authenticated_user: Optional[CustomUser] = authenticate(
                    request, email=user.email, password=password
                )
                if user is not None:
                    login(request, authenticated_user)
                    messages.success(request, "Пользователь успешно залогинен")
                    return redirect("main_page")
                else:
                    messages.error(request, "Ошибка аутентификации")

                return redirect("main_page")
    else:
        messages.error(request, "Не удалось получить токен")
    form = SetInitialPasswordForm()
    return render(
        request,
        "accounts/activate_staff_password.html",
        {
            "form": form,
            "title": "Активация приглашения",
        },
    )


@login_required
def remove_from_favorites(request: HttpRequest, product_id: int) -> HttpResponse:
    user = cast(CustomUser, request.user)
    Favorite.objects.filter(user=user, product_id=product_id).delete()
    return redirect("favorites")
