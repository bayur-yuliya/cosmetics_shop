import logging

import phonenumbers
from django.core.exceptions import ValidationError
from phonenumbers import carrier

from accounts.models import ActivationToken

logger = logging.getLogger(__name__)


def validate_phone_number(value: str) -> None:
    if not value:
        logger.debug("Phone validation skipped: empty value")
        return None
    try:
        phone = phonenumbers.parse(value, "UA")
        if not phonenumbers.is_valid_number(phone):
            logger.warning(f"Invalid phone number: {value}")
            raise ValidationError("Некорректный номер телефона")

        if carrier.name_for_number(phone, "ua") == "":
            logger.warning(f"Non-mobile phone number: {value}")
            raise ValidationError("Номер не принадлежит мобильному оператору")

    except phonenumbers.NumberParseException:
        logger.warning(f"Phone parse error: {value}")
        raise ValidationError("Неверный формат номера телефона")


def validate_activation_token(token_value: str) -> None:
    try:
        token_obj = ActivationToken.objects.get(token=token_value)
        if not token_obj.is_valid():
            logger.info(f"Expired activation token: user_id={token_obj.user_id}")
            token_obj.delete()
            raise ValidationError("Срок действия ссылки истёк.")
    except ActivationToken.DoesNotExist:
        logger.warning(f"Invalid activation token used: {token_value}")
        raise ValidationError("Токен недействителен.")
