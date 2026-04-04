import json
import logging

from django.contrib import messages
from django.db import transaction
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.csrf import csrf_exempt

from cosmetics_shop.forms import ClientForm, DeliveryAddressForm, PaymentForm
from cosmetics_shop.models import DeliveryAddress, Order, OrderItem, Payment, Status
from cosmetics_shop.services.cart_services import clear_cart_after_order
from cosmetics_shop.services.order_service import (
    create_order_from_cart,
    update_order_from_cart,
)
from cosmetics_shop.services.payment_service import (
    check_mono_payment_status,
    init_payment,
)
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

    if address_data.get("post_office"):
        form_delivery.fields["post_office"].initial = address_data["post_office"]

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
    try:
        cart = get_cart(request)
        if cart is None:
            return redirect("main_page")

        client_data = request.session.get("client_data", {})
        address_data = request.session.get("address_data", {})

        order_id = request.session.get("order_id")

        existing_order = None
        if order_id:
            existing_order = Order.objects.filter(
                id=order_id, status__in=[Status.NEW, Status.PAYMENT_FAILED]
            ).first()

        if existing_order:
            order = update_order_from_cart(
                existing_order, cart, client_data, address_data
            )
        else:
            order = create_order_from_cart(cart, client_data, address_data)
            request.session["order_id"] = order.id

        payment_method = request.session.get("payment_method", "card")

        if payment_method == "card":
            return redirect("pay_order", order_id=order.id)
        else:
            clear_cart_after_order(cart)
            return redirect("order_result")

    except OutOfStockError as e:
        messages.warning(request, str(e))
        return redirect("cart")
    except Exception as e:
        logger.error(f"Order processing error: {e}")
        messages.error(request, "Ошибка при оформлении заказа")
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
    if request.method != "POST":
        return HttpResponse(status=405)

    try:
        data = json.loads(request.body)
        invoice_id = data.get("invoiceId")

        if not invoice_id:
            return HttpResponse(status=400)

        # Безопасность: игнорируем status из payload, запрашиваем реальный у Моно
        if invoice_id is None:
            return

        real_status = check_mono_payment_status(invoice_id)

        if not real_status:
            return HttpResponse(status=400)

        with transaction.atomic():
            payment = (
                Payment.objects.select_related("order")
                .filter(external_id=invoice_id)
                .first()
            )

            if not payment:
                return HttpResponse(status=404)

            if payment.status == Payment.PaymentStatus.SUCCESS:
                return HttpResponse(status=200)

            if real_status == "success":
                payment.status = Payment.PaymentStatus.SUCCESS
                payment.save()
                payment.order.mark_as_paid()

                if payment.order.cart:
                    clear_cart_after_order(payment.order.cart)

            elif real_status in [
                "failure",
                "expired",
                "rejected",
                "canceled",
                "reversed",
            ]:
                payment.status = Payment.PaymentStatus.FAILED
                payment.save()
                payment.order.mark_as_failed_payment()

        return HttpResponse(status=200)

    except Exception as e:
        logger.error(f"Mono Webhook error: {e}")
        return HttpResponse(status=400)


@order_session_required
def order_result(request: HttpRequest) -> HttpResponse:
    order_id = request.session.get("order_id")

    if not order_id:
        messages.error(request, "Заказ не найден")
        return redirect("main_page")

    order = get_object_or_404(Order, pk=order_id)
    last_payment = order.payments.order_by("-created_at").first()

    if last_payment and last_payment.status == Payment.PaymentStatus.PENDING:
        invoice_id = last_payment.external_id
        if invoice_id is None:
            messages.error(request, "Ошибка оплаты")
            return redirect("delivery")

        real_status = check_mono_payment_status(invoice_id)

        if real_status == "success":
            last_payment.status = Payment.PaymentStatus.SUCCESS
            last_payment.save()
            order.mark_as_paid()

            if order.cart:
                clear_cart_after_order(order.cart)

        elif real_status in ["failure", "expired", "rejected", "canceled", "reversed"]:
            last_payment.status = Payment.PaymentStatus.FAILED
            last_payment.save()
            order.mark_as_failed_payment()

    products = OrderItem.objects.filter(order=order).select_related("product")

    status_context = {
        "is_paid": order.is_paid(),
        "is_failed": (
            last_payment.status == Payment.PaymentStatus.FAILED
            if last_payment
            else False
        ),
        "is_pending": (
            last_payment.status == Payment.PaymentStatus.PENDING
            if last_payment
            else True
        ),
        "payment_method": last_payment.method if last_payment else None,
    }

    if order.is_paid() or (
        last_payment and last_payment.method == Payment.PaymentMethod.CASH
    ):
        request.session.pop("order_id", None)

    return render(
        request,
        "cosmetics_shop/order_result.html",
        {
            "title": "Статус заказа",
            "order": order,
            "products": products,
            **status_context,
        },
    )
