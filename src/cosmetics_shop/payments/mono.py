import logging
from decimal import Decimal

import requests
from django.conf import settings
from django.db import transaction
from django.urls import reverse

from cosmetics_shop.models import Order, Payment
from cosmetics_shop.payments.mappers import MONO_STATUS_MAP

logger = logging.getLogger(__name__)


def map_mono_status(mono_status: str) -> str:
    return MONO_STATUS_MAP.get(mono_status, Payment.PaymentStatus.PENDING)


def create_mono_invoice(order: Order, redirect_url: str, webhook_url: str):
    headers = {
        "X-Token": str(settings.MONO_TOKEN),
        "Content-Type": "application/json",
    }

    payload = {
        "amount": int(order.total_price * Decimal("100")),
        "ccy": 980,  # UAH
        "redirectUrl": redirect_url,
        "webHookUrl": webhook_url,
        "merchantPaymInfo": {
            "reference": str(order.code),
            "destination": f"Оплата заказа {order.code}",
        },
    }

    response = requests.post(settings.MONO_URL, json=payload, headers=headers)
    response.raise_for_status()

    return response.json()


def init_payment(order: Order, request, custom_redirect_url: str | None = None):
    if custom_redirect_url:
        redirect_url = custom_redirect_url
    else:
        redirect_url = request.build_absolute_uri(reverse("order_result"))

    webhook_url = request.build_absolute_uri(reverse("mono_webhook"))

    invoice = create_mono_invoice(order, redirect_url, webhook_url)

    Payment.objects.update_or_create(
        order=order,
        method=Payment.PaymentMethod.CARD,
        defaults={
            "amount": order.total_price,
            "external_id": invoice.get("invoiceId"),
            "status": Payment.PaymentStatus.PENDING,
        },
    )

    return invoice.get("pageUrl")


def check_mono_payment_status(invoice_id: str) -> str | None:
    url = settings.MONO_URL_STATUS
    headers = {
        "X-Token": settings.MONO_TOKEN,
    }
    params = {"invoiceId": invoice_id}

    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        status = data.get("status")
        return status

    except requests.exceptions.RequestException as e:
        logger.error(f"Error checking Monobank status for {invoice_id}: {e}")
        return None


def sync_pending_payments():
    payments = Payment.objects.filter(status=Payment.PaymentStatus.PENDING)

    for payment in payments:
        invoice_id = payment.external_id

        if invoice_id is None:
            continue

        mono_payment_status = check_mono_payment_status(invoice_id)
        status = map_mono_status(mono_payment_status)

        with transaction.atomic():
            if status == Payment.PaymentStatus.SUCCESS:
                payment.status = Payment.PaymentStatus.SUCCESS
                payment.save()
                payment.order.mark_as_paid()

            elif status == Payment.PaymentStatus.FAILED:
                payment.status = Payment.PaymentStatus.FAILED
                payment.save()
                payment.order.mark_as_failed_payment()
