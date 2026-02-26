from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.urls import reverse

from accounts.models import CustomUser, ActivationToken
from accounts.utils.validators import validate_activation_token
from config import settings
from config.settings import DEFAULT_STAFF_GROUP_NAME


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
