import logging

from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.urls import reverse

logger = logging.getLogger(__name__)


class NotificationService:
    @staticmethod
    def _send_email(
        subject: str,
        template_name: str,
        context: dict,
        recipient_list: list,
        message: str = "",
    ):
        """Base method for email send HTML-messages"""
        try:
            html_message = render_to_string(template_name, context)

            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=recipient_list,
                html_message=html_message,
                fail_silently=False,
            )
            logger.info(f"Email '{subject}' sent to {recipient_list}")
        except Exception as e:
            logger.exception(
                f"Failed to send email '{subject}' to {recipient_list}: {e}"
            )

    @classmethod
    def send_staff_invitation(cls, invitation):
        path = reverse("activate")
        activation_url = f"{settings.SITE_URL}{path}?token={invitation.token}"

        context = {
            "activation_url": activation_url,
            "expires_at": invitation.expires_at.strftime("%Y-%m-%d %H:%M"),
        }

        cls._send_email(
            subject="Активация аккаунта сотрудника",
            template_name="cosmetics_shop/emails/staff_invitation.html",
            context=context,
            recipient_list=[invitation.email],
        )

    @classmethod
    def send_order_success(cls, order):
        context = {
            "order": order,
            "items": order.order_items.all(),
        }

        cls._send_email(
            subject=f"Заказ №{order.id} успешно оплачен",
            template_name="cosmetics_shop/emails/order_success.html",
            context=context,
            recipient_list=[order.snapshot_email or order.client.email],
        )
