import logging

from celery import shared_task
from django.utils import timezone

from accounts.utils.account_services import anonymize_client, has_active_orders
from cosmetics_shop.models import Client, Order, Status

logger = logging.getLogger(__name__)


@shared_task
def process_client_anonymization():
    logger.info("Start client anonymization task")

    now = timezone.now()
    clients_to_anonymize = Client.objects.filter(
        is_active=True, deletion_scheduled_date__lte=now
    )

    for client in clients_to_anonymize.iterator():
        if not has_active_orders(client):
            logger.info(f"Anonymizing client: client_id={client.id}")
            anonymize_client(client)
        else:
            logger.warning(
                f"Client still has active orders, reset deletion: client_id={client.id}"
            )
            client.deletion_scheduled_date = None
            client.is_pending_deletion = False
            client.save(
                update_fields=["deletion_scheduled_date", "is_pending_deletion"]
            )

    logger.info("Finished client anonymization task")


@shared_task
def update_pending_deletion_dates():
    logger.info("Start updating deletion dates")

    pending_clients = Client.objects.filter(
        is_pending_deletion=True, deletion_scheduled_date__isnull=True
    )

    for client in pending_clients.iterator():
        if not has_active_orders(client):
            logger.debug(f"Processing client: client_id={client.id}")

            last_order = (
                Order.objects.filter(client=client, status=Status.COMPLETED)
                .order_by("-completed_at")
                .first()
            )

            if last_order:
                client.deletion_scheduled_date = (
                    last_order.completed_at + timezone.timedelta(days=14)
                )
                client.save(update_fields=["deletion_scheduled_date"])
                logger.info(f"Deletion date set: client_id={client.id}")
            else:
                logger.info(f"No orders, anonymizing: client_id={client.id}")
                anonymize_client(client)

    logger.info("Finished updating deletion dates")
