import logging

from django.contrib import messages
from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from cosmetics_shop.forms import ClientForm, DeliveryAddressForm
from cosmetics_shop.models import DeliveryAddress, Order, OrderItem
from cosmetics_shop.services.order_service import create_order_from_cart
from cosmetics_shop.utils.cart_utils import get_cart
from cosmetics_shop.utils.client_utils import get_client, process_delivery_data
from cosmetics_shop.utils.decorators import cart_required, order_session_required
from utils.custom_exceptions import OutOfStockError
from utils.custom_types import AuthenticatedRequest

logger = logging.getLogger(__name__)


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
    logger.info(f"Create order started: user_id={request.user.id}")

    try:
        cart = get_cart(request)
        client_data = request.session.get("client_data", {})
        address_data = request.session.get("address_data", {})
        order = create_order_from_cart(cart, client_data, address_data)
        request.session["order_id"] = order.id

        logger.info(f"Order created successfully: order_id={order.id}")
        return redirect("order_success")

    except OutOfStockError as e:
        logger.warning(f"Order failed (stock): {str(e)}")
        messages.warning(request, str(e))
        return redirect("cart")

    except ValueError as e:
        logger.exception(f"Unexpected error during order creation: {str(e)}")
        messages.error(request, "Ошибка при создании заказа")
        return redirect("delivery")


@order_session_required
def order_success(request: HttpRequest) -> HttpResponse:
    order_id: int | None = request.session.get("order_id")

    if order_id:
        logger.info(f"Order success page: order_id={order_id}")

        order: Order = get_object_or_404(Order, pk=order_id)
        products: QuerySet[OrderItem] = OrderItem.objects.filter(
            order=order
        ).select_related("product")
        del request.session["order_id"]
    else:
        logger.error("Order success page without order_id in session")
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
