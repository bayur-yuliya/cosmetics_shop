from decimal import Decimal

import requests
from django.conf import settings
from django.urls import reverse

from cosmetics_shop.models import Order, Payment


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


def init_payment(order: Order, request):
    redirect_url = request.build_absolute_uri(reverse("order_success"))
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
