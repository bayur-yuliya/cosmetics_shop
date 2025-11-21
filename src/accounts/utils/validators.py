import phonenumbers
from django.contrib import messages
from django.shortcuts import redirect
from phonenumbers import carrier
from django.core.exceptions import ValidationError

from accounts.models import ActivationToken


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


def validate_activation_token(request, token_value):
    try:
        token_obj = ActivationToken.objects.get(token=token_value)
    except ActivationToken.DoesNotExist:
        messages.error(request, "Токен недействителен.")
        return redirect("main_page")

    if not token_obj.is_valid():
        messages.error(request, "Срок действия ссылки истёк.")
        token_obj.delete()
