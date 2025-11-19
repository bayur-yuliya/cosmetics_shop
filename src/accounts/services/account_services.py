from django.core.mail import send_mail
from django.urls import reverse


def send_activation_email(user, token_obj):
    try:
        activation_url = f"http://127.0.0.1:8000{reverse('activate')}?token={token_obj.token}"

        subject = "Активация аккаунта"

        message = (
            f"Вас добавили в систему магазина.\n\n"
            f"Чтобы активировать аккаунт и установить пароль, перейдите по ссылке:\n"
            f"{activation_url}\n\n"
            f"Ссылка действительна до: {token_obj.expires_at.strftime('%Y-%m-%d %H:%M')}"
        )

        send_mail(
            subject,
            message,
            "noreply@gmail.com",
            [user.email],
            fail_silently=False,
        )

    except Exception as e:
        print(f"Exception: {e}")
