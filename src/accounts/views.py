import uuid

from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db import transaction
from django.shortcuts import render, redirect

from accounts.forms import ClientCreationForm
from cosmetics_shop.models import Client, Favorite, Order, OrderItem, OrderStatusLog


@login_required
def logout_view(request):
    logout(request)
    return redirect("main_page")


@login_required
@transaction.atomic
def delete_account(request):
    user = request.user

    user.username = f"deleted_user_{uuid.uuid4().hex[:8]}"
    user.email = ""
    user.first_name = ""
    user.last_name = ""

    user.is_active = False
    user.save()

    logout(request)

    return redirect("main_page")


@login_required
def user_contact(request):
    title = 'Контактная информация'
    client, created = Client.objects.get_or_create(user=request.user)
    if request.method == "POST":
        form = ClientCreationForm(request.POST, instance=client, initial={"email": request.user.email})
        if form.is_valid():
            form.save()
            return redirect("user_contact")
    form = ClientCreationForm(instance=client, initial={"email": request.user.email})
    return render(
        request, "accounts/user_contact.html", {"title": title, "form": form, "client": client}
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

