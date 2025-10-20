import phonenumbers
from phonenumbers import carrier
from django.core.exceptions import ValidationError


def validate_phone_number(value):
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
