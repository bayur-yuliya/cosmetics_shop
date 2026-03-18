import uuid

from allauth.account.models import EmailAddress
from allauth.socialaccount.models import SocialAccount
from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils import timezone

from accounts.models import ActivationToken, CustomUser
from accounts.utils.validators import validate_activation_token
from config import settings
from config.settings.base import DEFAULT_STAFF_GROUP_NAME
from cosmetics_shop.models import Client, DeliveryAddress, Order, Status


def send_activation_email(user: CustomUser, token_obj: ActivationToken) -> None:
    try:
        path = reverse("activate")

        activation_url = f"{settings.SITE_URL}{path}?token={token_obj.token}"

        subject = "Активация аккаунта"

        message = (
            f"Вас добавили в систему магазина.\n\n"
            f"Чтобы активировать аккаунт и установить пароль, перейдите по ссылке:\n"
            f"{activation_url}\n\n"
            f"Ссылка действительна до: "
            f"{token_obj.expires_at.strftime('%Y-%m-%d %H:%M')}"
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


def activate_user(token: str, password: str) -> CustomUser | None:
    try:
        validate_activation_token(token)
    except ValidationError:
        return None

    with transaction.atomic():
        token_obj: ActivationToken = (
            ActivationToken.objects.select_for_update()
            .select_related("user")
            .get(token=token)
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

        EmailAddress.objects.filter(user=client.user).delete()
        SocialAccount.objects.filter(user=client.user).delete()

    Client.objects.filter(pk=client.pk).update(
        first_name="Аноним",
        last_name="",
        phone="",
        email=new_email,
        is_active=False,
        is_pending_deletion=False,
    )

    DeliveryAddress.objects.filter(client=client).delete()

    # These snapshots are of no value to the tax authorities,
    # so we will also anonymize them.
    Order.objects.filter(client=client).update(
        snapshot_name="Анонимный клиент",
        snapshot_phone="",
        snapshot_email="",
        snapshot_address="Адрес удалён",
    )


def has_active_orders(client: Client) -> bool:
    availability_of_active_orders = (
        Order.objects.filter(client=client, completed_at=None)
        .exclude(status__in=[Status.COMPLETED, Status.CANCELED])
        .exists()
    )
    print(availability_of_active_orders)
    return availability_of_active_orders


def delete_client(client: Client) -> None:
    if has_active_orders(client):
        client.is_pending_deletion = True
        client.deletion_scheduled_date = None
        client.save()

    else:
        last_order = (
            Order.objects.filter(client=client, status=Status.COMPLETED)
            .order_by("-completed_at")
            .first()
        )

        if not last_order:
            anonymize_client(client)
            return None

        order_return_period = last_order.completed_at + timezone.timedelta(days=14)
        now = timezone.now()

        if now < order_return_period:
            client.is_pending_deletion = True
            client.deletion_scheduled_date = order_return_period
            client.save()
        else:
            anonymize_client(client)
            return None
