import logging
import uuid

from allauth.account.models import EmailAddress
from allauth.socialaccount.models import SocialAccount
from django.conf import settings
from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils import timezone

from accounts.models import ActivationToken, CustomUser
from accounts.utils.validators import validate_activation_token
from config.settings.base import DEFAULT_STAFF_GROUP_NAME
from cosmetics_shop.models import Client, DeliveryAddress, Order, Status

logger = logging.getLogger(__name__)


def send_activation_email(user: CustomUser, token_obj: ActivationToken) -> None:
    try:
        path = reverse("activate")
        activation_url = f"{settings.SITE_URL}{path}?token={token_obj.token}"

        logger.debug(f"Sending activation email: user_id={user.id}")

        subject = "Активация аккаунта"

        message = (
            f"Вас добавили в систему магазина.\n\n"
            f"Чтобы активировать аккаунт и установить пароль, перейдите по ссылке:\n"
            f"{activation_url}\n\n"
            f"Ссылка действительна до: "
            f"{token_obj.expires_at.strftime('%Y-%m-%d %H:%M')}"
        )

        logger.info(f"Activation email sent: user_id={user.id}")

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
        logger.exception(
            f"Failed to send activation email: user_id={user.id}, error={str(e)}"
        )


def activate_user(token: str, password: str) -> CustomUser | None:
    logger.debug("Activation attempt started")

    try:
        validate_activation_token(token)
    except ValidationError:
        logger.warning("Activation failed: invalid or expired token")
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

        logger.info(f"User activated: user_id={user.id}")

    return user


def anonymize_client(client: Client):
    logger.info(f"Anonymizing client: client_id={client.id}")

    new_email = f"deleted_{client.id}_{uuid.uuid4().hex[:10]}@deleted.invalid"

    if client.user:
        logger.debug(f"Anonymizing user: user_id={client.user.id}")

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

    logger.info(f"Client anonymized: client_id={client.id}")


def has_active_orders(client: Client) -> bool:
    availability_of_active_orders = (
        Order.objects.filter(client=client, completed_at=None)
        .exclude(status__in=[Status.COMPLETED, Status.CANCELED])
        .exists()
    )

    logger.debug(
        f"Active orders check: client_id={client.id},"
        f" result={availability_of_active_orders}"
    )

    return availability_of_active_orders


def delete_client(client: Client) -> None:
    logger.info(f"Delete client requested: client_id={client.id}")

    if has_active_orders(client):
        logger.warning(f"Client has active orders: client_id={client.id}")

        client.is_pending_deletion = True
        client.deletion_scheduled_date = None
        client.save()
        return

    else:
        last_order = (
            Order.objects.filter(client=client, status=Status.COMPLETED)
            .order_by("-completed_at")
            .first()
        )

        if not last_order:
            logger.info(
                f"No orders found, anonymizing immediately:" f" client_id={client.id}"
            )
            anonymize_client(client)
            return None

        order_return_period = last_order.completed_at + timezone.timedelta(days=14)
        now = timezone.now()

        if now < order_return_period:
            logger.info(
                f"Client scheduled for deletion: client_id={client.id},"
                f" date={order_return_period}"
            )

            client.is_pending_deletion = True
            client.deletion_scheduled_date = order_return_period
            client.save()
        else:
            logger.info(f"Return period passed, anonymizing: client_id={client.id}")
            anonymize_client(client)
            return None
