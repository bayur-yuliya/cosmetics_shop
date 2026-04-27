import logging
from datetime import timedelta

from celery import shared_task
from django.db import transaction
from django.utils import timezone

from cosmetics_shop.models import Order, Payment, Status
from cosmetics_shop.payments.mono import check_mono_payment_status, map_mono_status
from cosmetics_shop.services.cart_services import clear_cart_after_order
from cosmetics_shop.services.product_service import restore_stock_product

logger = logging.getLogger(__name__)


@shared_task
def sync_pending_payments():
    payments = Payment.objects.filter(status=Payment.PaymentStatus.PENDING)

    for payment in payments:
        invoice_id = payment.external_id

        if invoice_id is None:
            continue

        mono_payment_status = check_mono_payment_status(invoice_id)
        if mono_payment_status:
            status = map_mono_status(mono_payment_status)
        else:
            status = Payment.PaymentStatus.PENDING

        with transaction.atomic():
            if status == Payment.PaymentStatus.SUCCESS:
                payment.status = Payment.PaymentStatus.SUCCESS
                payment.save()
                payment.order.mark_as_paid()

            elif status == Payment.PaymentStatus.FAILED:
                payment.status = Payment.PaymentStatus.FAILED
                payment.save()
                payment.order.mark_as_failed_payment()


@shared_task
def cleanup_expired_orders():
    """
    Cancels unpaid orders created more than 45 minutes ago
    and returns the items to the warehouse.
    Payment session monobank: Typically active for 15-30 minutes.
    """
    expiry_threshold = timezone.now() - timedelta(minutes=45)
    expired_orders = (
        Order.objects.filter(
            status__in=[Status.NEW, Status.PAYMENT_FAILED],
            created_at__lt=expiry_threshold,
        )
        .exclude(payments__method=Payment.PaymentMethod.CASH)
        .distinct()
    )

    if not expired_orders.exists():
        return "No expired orders found."

    count = 0
    for order in expired_orders.iterator():
        try:
            with transaction.atomic():
                order = Order.objects.select_for_update(skip_locked=True).get(
                    pk=order.pk
                )

                if order.is_paid():
                    continue

                logger.info(f"Expiring order {order.code}...")

                for item in order.order_items.select_related("product"):
                    if item.product:
                        restore_stock_product(item.product.code, item.quantity)
                        logger.debug(f"Restored {item.quantity} of {item.product.name}")

                order.set_status(
                    new_status=Status.CANCELED,
                    comment="Order expired: payment not received within 30 minutes.",
                )

                order.payments.filter(status=Payment.PaymentStatus.PENDING).update(
                    status=Payment.PaymentStatus.FAILED
                )

                count += 1

        except Exception as e:
            logger.error(f"Failed to expire order {order.code}: {e}")

    return f"Successfully expired {count} orders."


@shared_task(bind=True, max_retries=3)
def process_mono_webhook(self, invoice_id: str):
    try:
        real_status = check_mono_payment_status(invoice_id)

        if not real_status:
            return

        with transaction.atomic():
            payment = (
                Payment.objects.select_related("order")
                .select_for_update()
                .filter(external_id=invoice_id)
                .first()
            )

            if not payment:
                return

            if payment.status == Payment.PaymentStatus.SUCCESS:
                return

            status = map_mono_status(real_status)

            if status == Payment.PaymentStatus.SUCCESS:
                payment.status = status
                payment.save(update_fields=["status"])

                payment.order.mark_as_paid()

                if payment.order.cart:
                    clear_cart_after_order(payment.order.cart)

            elif status == Payment.PaymentStatus.FAILED:
                payment.status = status
                payment.save(update_fields=["status"])

                payment.order.mark_as_failed_payment()

    except Exception as exc:
        logger.error(f"Webhook task error: {exc}")
        raise self.retry(exc=exc, countdown=60)
