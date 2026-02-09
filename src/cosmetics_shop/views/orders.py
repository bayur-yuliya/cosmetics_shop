from django.contrib import messages
from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render

from cosmetics_shop.forms import ClientForm, DeliveryAddressForm
from cosmetics_shop.models import DeliveryAddress, Client, Order, OrderItem
from cosmetics_shop.services.order_service import get_client, create_order_from_cart
from cosmetics_shop.utils.decorators import cart_required, order_session_required


@cart_required
def delivery(request: HttpRequest) -> HttpResponse:
    try:
        client = get_client(request)
        last_address: DeliveryAddress | None = (
            DeliveryAddress.objects.filter(client=client).order_by("-id").first()
        )
    except Client.DoesNotExist:
        client = None
        last_address = None

    if request.method == "POST":
        form = ClientForm(request.POST, instance=client)
        form_delivery = DeliveryAddressForm(request.POST, instance=last_address)

        if form.is_valid() and form_delivery.is_valid():
            new_client = form.save()
            if request.user.is_authenticated:
                new_client.user = request.user
                new_client.save()

            address = form_delivery.save(commit=False)
            address.client = client
            address.save()
            return redirect("order", address_id=address.id)

    form = ClientForm(instance=client)
    form_delivery = DeliveryAddressForm(instance=last_address)

    return render(
        request,
        "cosmetics_shop/delivery.html",
        {
            "title": "Оформление заказа",
            "form": form,
            "form_delivery": form_delivery,
        },
    )


@cart_required
def create_order(request: HttpRequest, address_id: int) -> HttpResponse:
    order = create_order_from_cart(request, address_id)
    if order:
        request.session["order_id"] = order.id
        return redirect("order_success")
    return redirect("delivery")


@order_session_required
def order_success(request: HttpRequest) -> HttpResponse:
    order_id: int | None = request.session.get("order_id")

    if order_id:
        order: Order = Order.objects.get(pk=order_id)
        products: QuerySet[OrderItem] = OrderItem.objects.filter(order=order)
        del request.session["order_id"]
    else:
        messages.error(request, "Возникла проблема с сохранением заказа")
        return redirect("main_page")

    return render(
        request,
        "cosmetics_shop/order_success.html",
        {
            "title": "Заказ",
            "order": order,
            "products": products,
            "status": "Заказ успешно обработан",
        },
    )
