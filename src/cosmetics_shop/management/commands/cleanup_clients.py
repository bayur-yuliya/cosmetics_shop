from django.core.management import BaseCommand
from django.utils import timezone

from accounts.utils.account_services import anonymize_client
from cosmetics_shop.models import Client


class Command(BaseCommand):
    help = "Автоматическая анонимизация клиентов по расписанию"

    def handle(self, *args, **options):
        now = timezone.now()

        pending_clients = Client.objects.filter(
            is_pending_deletion=True,
            deletion_scheduled_date__lte=now
        )

        three_years_ago = now - timezone.timedelta(days=365 * 3)
        old_guests = Client.objects.filter(
            user__isnull=True,
            is_active=True
        ).exclude(
            order__created_at__gte=three_years_ago
        )

        targets = pending_clients | old_guests
        count = targets.count()

        for client in targets:
            anonymize_client(client)

        self.stdout.write(self.style.SUCCESS(f"Successfully! {count} old guests id anonymize."))
