import uuid

from allauth.account.models import EmailAddress
from allauth.account.views import login
from allauth.socialaccount.models import SocialAccount
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.core.paginator import Paginator
from django.db import transaction
from django.shortcuts import render, redirect

from accounts.forms import (
    ClientCreationForm,
    AdminCreateUserForm,
    SetInitialPasswordForm,
)
from accounts.models import ActivationToken
from accounts.utils.validators import validate_activation_token
from cosmetics_shop.models import Client, Favorite, Order, OrderItem, OrderStatusLog


@login_required
def logout_view(request):
    logout(request)
    return redirect("main_page")


@login_required
@transaction.atomic
def delete_account(request):
    user = request.user

    SocialAccount.objects.filter(user=user).delete()
    EmailAddress.objects.filter(user=user).delete()

    user.username = f"deleted_user_{uuid.uuid4().hex[:8]}"
    user.email = None
    user.first_name = ""
    user.last_name = ""

    user.is_active = False
    user.save()
    user.set_unusable_password()

    logout(request)
    cache.clear()
    return redirect("main_page")


@login_required
def user_contact(request):
    title = "Контактная информация"
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
        {"title": title, "form": form, "client": client},
    )


@login_required
def favorites(request):
    products = Favorite.objects.filter(user=request.user)

    paginator = Paginator(products, 20)
    page_number = request.GET.get("page")
    products = paginator.get_page(page_number)

    return render(
        request,
        "accounts/favorites.html",
        {
            "title": "Избранное",
            "products": products,
            "is_favorite": True,
        },
    )


@login_required
def order_history(request):
    title = "История заказов"
    client, _ = Client.objects.get_or_create(user=request.user)
    orders = Order.objects.filter(client=client)
    order_items = []

    for order in orders:
        dictt = {}
        dictt["order"] = order
        dictt["item"] = []
        items = OrderItem.objects.filter(order=order.id)
        dictt["status"] = OrderStatusLog.objects.filter(order=order)[0]
        if items.count() > 1:
            for item in items:
                dictt["order"] = order
                dictt["item"] += [item]
        else:
            dictt["item"] = items
        order_items.append(dictt)
    return render(
        request,
        "accounts/order_history.html",
        {
            "title": title,
            "order_items": order_items,
        },
    )


@staff_member_required
def create_staff_user(request):
    if request.method == "POST":
        form = AdminCreateUserForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("main_page")
    form = AdminCreateUserForm()
    return render(request, "accounts/create_staff_user.html", {"form": form})


def activate_account(request):
    token_value = request.GET.get("token")

    validate_activation_token(request, token_value)
    token_obj = ActivationToken.objects.get(token=token_value)

    user = token_obj.user
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

            user = authenticate(request, email=user.email, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, "Пользователь успешно залогинен")
                return redirect("main_page")
            else:
                messages.error(request, "Ошибка аутентификации")

            return redirect("main_page")

    form = SetInitialPasswordForm()
    return render(
        request,
        "accounts/activate_staff_password.html",
        {
            "form": form,
        },
    )


@login_required
def remove_from_favorites(request, product_id):
    Favorite.objects.filter(user=request.user, product_id=product_id).delete()
    return redirect("favorites")
