from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import ActivationToken
from accounts.utils.account_services import send_activation_email

User = get_user_model()


@receiver(post_save, sender=User)
def send_activation_after_create(sender, instance, created, **kwargs):
    if created and not instance.is_active:
        token = ActivationToken.create_for_user(instance)
        send_activation_email(instance, token)
