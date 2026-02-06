from django.contrib import messages
from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect
from django.urls import reverse

from accounts.models import CustomUser, ActivationToken
from accounts.utils.validators import validate_activation_token
from config import settings


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


def activate_user_service(request, token_value: str, password: str) -> CustomUser:
    try:
        validate_activation_token(token_value)
    except ValidationError as e:
        messages.error(request, e.message)

    token_obj: ActivationToken = ActivationToken.objects.select_related("user").get(
        token=token_value
    )

    user: CustomUser = token_obj.user
    user.set_password(password)
    user.is_active = True
    user.is_staff = True

    groups = Group.objects.get(name="Гости")
    user.groups.add(groups)

    user.save()
    token_obj.delete()

    messages.success(request, "Аккаунт активирован!")
    return user


def login_authenticated_user(
    request: HttpRequest, user: CustomUser, password: str
) -> HttpResponse:
    from django.contrib.auth import authenticate

    authenticated_user: CustomUser | None = authenticate(
        request, email=user.email, password=password
    )

    if user is not None:
        from django.contrib.auth import login

        login(request, authenticated_user)
        messages.success(request, "Пользователь успешно залогинен")
        return redirect("main_page")
    else:
        messages.error(request, "Ошибка аутентификации")
    return redirect("main_page")
