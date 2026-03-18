import phonenumbers
from django.core.exceptions import ValidationError
from phonenumbers import carrier

from accounts.models import ActivationToken


def validate_phone_number(value: str) -> None:
    if not value:
        return None
    try:
        phone = phonenumbers.parse(value, "UA")
        if not phonenumbers.is_valid_number(phone):
            raise ValidationError("Некорректный номер телефона")

        if carrier.name_for_number(phone, "ua") == "":
            raise ValidationError("Номер не принадлежит мобильному оператору")

    except phonenumbers.NumberParseException:
        raise ValidationError("Неверный формат номера телефона")


def validate_activation_token(token_value: str) -> None:
    try:
        token_obj = ActivationToken.objects.get(token=token_value)
        if not token_obj.is_valid():
            token_obj.delete()
            raise ValidationError("Срок действия ссылки истёк.")
    except ActivationToken.DoesNotExist:
        raise ValidationError("Токен недействителен.")
