import uuid

from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils import timezone

from accounts.models import CustomUser, ActivationToken
from accounts.utils.validators import validate_activation_token
from config import settings
from config.settings import DEFAULT_STAFF_GROUP_NAME
from cosmetics_shop.models import Client, Order, Status


def send_activation_email(user: CustomUser, token_obj: ActivationToken) -> None:
    try:
        path = reverse("activate")

        activation_url = f"{settings.SITE_URL}{path}?token={token_obj.token}"

        subject = "Активация аккаунта"

        message = (
            f"Вас добавили в систему магазина.\n\n"
            f"Чтобы активировать аккаунт и установить пароль, перейдите по ссылке:\n"
            f"{activation_url}\n\n"
            f"Ссылка действительна до: {token_obj.expires_at.strftime('%Y-%m-%d %H:%M')}"
        )

        if user.email is not None:
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=False,
            )
        else:
            raise ValueError("Не определен email пользователя")

    except Exception as e:
        print(f"Ошибка отправки письма: {e}")


def activate_user_service(token_value: str, password: str) -> CustomUser | None:
    try:
        validate_activation_token(token_value)
    except ValidationError:
        return None

    with transaction.atomic():
        token_obj: ActivationToken = ActivationToken.objects.select_for_update().select_related("user").get(
            token=token_value
        )

        user: CustomUser = token_obj.user
        user.set_password(password)
        user.is_active = True
        user.is_staff = True

        groups = get_object_or_404(Group, name=DEFAULT_STAFF_GROUP_NAME)
        user.groups.add(groups)

        user.save()
        token_obj.delete()
    return user


def anonymize_client(client: Client):
    new_email = f"deleted_{client.id}_{uuid.uuid4().hex[:10]}@deleted.invalid"

    if client.user:
        client.user.email = new_email
        client.user.is_active = False
        client.user.save(update_fields=["email", "is_active"])

    Client.objects.filter(pk=client.pk).update(
        first_name="Аноним",
        last_name="",
        phone="",
        email=new_email,
        is_active=False,
        is_pending_deletion=False
    )

    # These snapshots are of no value to the tax authorities, so we will also anonymize them.
    Order.objects.filter(client=client).update(
        snapshot_name="Анонимный клиент",
        snapshot_phone="",
        snapshot_email="",
        snapshot_address="Адрес удалён"
    )


def has_active_orders(client: Client) -> bool:
    return Order.objects.filter(client=client).exclude(status__in=[Status.COMPLETED, Status.CANCELED]).exists()


def calculate_deletion_date(client: Client) -> timezone.datetime:
    completed_orders = Order.objects.filter(client=client, status=Status.COMPLETED).order_by('-delivery_date')
    if completed_orders.exists():
        last_delivery = completed_orders.first().delivery_date
        return last_delivery + timezone.timedelta(days=14)
    else:
        return timezone.now() + timezone.timedelta(days=365 * 3)


def delete_client(client: Client) -> None:
    if has_active_orders(client):
        client.is_pending_deletion = True
        client.deletion_scheduled_date = None
    else:
        scheduled_date = calculate_deletion_date(client)
        if scheduled_date <= timezone.now():
            anonymize_client(client)
        else:
            client.is_pending_deletion = True
            client.deletion_scheduled_date = scheduled_date
    client.save()


# Для cron/Celery task: ежедневно проверять и анонимизировать
# def process_pending_deletions() -> None:
#     now = timezone.now()
#     for client in Client.objects.filter(is_pending_deletion=True):
#         if has_active_orders(client):
#             continue  # Ждем
#         scheduled_date = client.deletion_scheduled_date or calculate_deletion_date(client)
#         if scheduled_date <= now:
#             anonymize_client(client)
#         else:
#             client.deletion_scheduled_date = scheduled_date
#             client.save()
