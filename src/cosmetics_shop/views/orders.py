import json
import logging

from django.contrib import messages
from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.csrf import csrf_exempt

from cosmetics_shop.forms import ClientForm, DeliveryAddressForm, PaymentForm
from cosmetics_shop.models import DeliveryAddress, Order, OrderItem, Payment
from cosmetics_shop.services.order_service import create_order_from_cart
from cosmetics_shop.services.payment_service import init_payment
from cosmetics_shop.utils.cart_utils import get_cart
from cosmetics_shop.utils.client_utils import get_client, process_delivery_data
from cosmetics_shop.utils.decorators import cart_required, order_session_required
from utils.custom_exceptions import OutOfStockError
from utils.custom_types import AuthenticatedRequest

logger = logging.getLogger(__name__)


@cart_required
def delivery(request: HttpRequest) -> HttpResponse:
    client = get_client(request)
    last_address = DeliveryAddress.objects.filter(client=client).order_by("id").last()

    client_data = request.session.get("client_data", {})
    address_data = request.session.get("address_data", {})
    saved_payment = request.session.get("payment_method", "card")

    if request.method == "POST":
        address = process_delivery_data(
            request, client=client, last_address=last_address
        )
        payment_form = PaymentForm(request.POST)

        if payment_form.is_valid():
            request.session["payment_method"] = payment_form.cleaned_data["method"]

        if address is not None and payment_form.is_valid():
            return redirect("order")
    else:
        payment_form = PaymentForm(initial={"method": saved_payment})

    form = ClientForm(instance=client, initial=client_data)
    form_delivery = DeliveryAddressForm(instance=last_address, initial=address_data)

    return render(
        request,
        "cosmetics_shop/delivery.html",
        {
            "title": "Оформление заказа",
            "form": form,
            "form_delivery": form_delivery,
            "payment_form": payment_form,
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
        payment_method = request.session.get("payment_method", "card")

        if payment_method == "card":
            return redirect("pay_order", order_id=order.id)

        logger.info(f"Order created successfully: order_id={order.id}")
        return redirect("order_success")

    except OutOfStockError as e:
        messages.warning(request, str(e))
        return redirect("cart")
    except ValueError:
        messages.error(request, "Ошибка при создании заказа")
        return redirect("delivery")


def pay_order(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    try:
        payment_url = init_payment(order, request)
        return redirect(payment_url)
    except Exception as e:
        logger.error(f"MonoBank Init Error: {e}")
        messages.error(request, "Сервис оплаты временно недоступен. Попробуйте позже.")
        return redirect("delivery")


@csrf_exempt
def mono_webhook(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            invoice_id = data.get("invoiceId")
            status = data.get("status")

            if invoice_id and status:
                payment = Payment.objects.filter(external_id=invoice_id).first()
                if payment:
                    if status == "success":
                        payment.status = Payment.PaymentStatus.SUCCESS
                        payment.save()
                        payment.order.mark_as_paid()

                    elif status in ["failure", "expired", "rejected"]:
                        payment.status = Payment.PaymentStatus.FAILED
                        payment.save()
            return HttpResponse(status=200)
        except Exception as e:
            logger.error(f"Mono Webhook error: {e}")
            return HttpResponse(status=400)

    return HttpResponse(status=405)


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
