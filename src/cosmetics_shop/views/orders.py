from django.contrib import messages
from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render, get_object_or_404

from cosmetics_shop.forms import ClientForm, DeliveryAddressForm
from cosmetics_shop.models import DeliveryAddress, Order, OrderItem
from cosmetics_shop.services.order_service import create_order_from_cart
from cosmetics_shop.utils.decorators import cart_required, order_session_required
from cosmetics_shop.services.client_service import process_delivery_data, get_client
from utils.custom_exceptions import OutOfStockError
from utils.custom_types import AuthenticatedRequest


@cart_required
def delivery(request: HttpRequest) -> HttpResponse:
    client = get_client(request)

    last_address: DeliveryAddress | None = (
        DeliveryAddress.objects.filter(client=client).order_by("id").last()
    )

    client_data = request.session.get("client_data", {})
    address_data = request.session.get("address_data", {})

    if request.method == "POST":
        address = process_delivery_data(
            request, client=client, last_address=last_address
        )

        if address is not None:
            return redirect("order")

    form = ClientForm(instance=client, initial=client_data)
    form_delivery = DeliveryAddressForm(instance=last_address, initial=address_data)

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
def create_order(request: AuthenticatedRequest) -> HttpResponse:
    try:
        order = create_order_from_cart(request)
        request.session["order_id"] = order.id
        return redirect("order_success")

    except OutOfStockError as e:
        messages.warning(request, str(e))
        return redirect("cart")

    except ValueError as e:
        messages.error(request, str(e))
        return redirect("delivery")


@order_session_required
def order_success(request: HttpRequest) -> HttpResponse:
    order_id: int | None = request.session.get("order_id")

    if order_id:
        order: Order = get_object_or_404(Order, pk=order_id)
        products: QuerySet[OrderItem] = OrderItem.objects.filter(order=order).select_related("product")
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
