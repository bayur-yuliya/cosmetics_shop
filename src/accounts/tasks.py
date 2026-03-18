from celery import shared_task
from django.utils import timezone

from accounts.utils.account_services import anonymize_client, has_active_orders
from cosmetics_shop.models import Client, Order, Status


@shared_task
def process_client_anonymization():
    now = timezone.now()
    clients_to_anonymize = Client.objects.filter(
        is_active=True, deletion_scheduled_date__lte=now
    )

    for client in clients_to_anonymize.iterator():
        if not has_active_orders(client):
            anonymize_client(client)
        else:
            client.deletion_scheduled_date = None
            client.is_pending_deletion = False
            client.save(
                update_fields=["deletion_scheduled_date", "is_pending_deletion"]
            )


@shared_task
def update_pending_deletion_dates():
    pending_clients = Client.objects.filter(
        is_pending_deletion=True, deletion_scheduled_date__isnull=True
    )

    for client in pending_clients.iterator():
        if not has_active_orders(client):
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
            else:
                anonymize_client(client)
