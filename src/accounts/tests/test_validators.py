import pytest
from django.core.exceptions import ValidationError

from accounts.models import ActivationToken
from accounts.utils.validators import validate_activation_token, validate_phone_number


def test_validate_phone_number_valid():
    # Valid Ukrainian mobile number
    validate_phone_number("+380671234567")


def test_validate_phone_number_invalid_number():
    with pytest.raises(ValidationError) as exc:
        validate_phone_number("+380000000000")

    assert "Некорректный номер телефона" in str(exc.value)


def test_validate_phone_number_invalid_format():
    with pytest.raises(ValidationError) as exc:
        validate_phone_number("invalid_phone")

    assert "Неверный формат номера телефона" in str(exc.value)


def test_validate_phone_number_not_mobile(monkeypatch):
    def mock_name_for_number(phone, lang):
        return ""

    monkeypatch.setattr(
        "accounts.utils.validators.carrier.name_for_number",
        mock_name_for_number,
    )

    with pytest.raises(ValidationError) as exc:
        validate_phone_number("+380671234567")

    assert "Номер не принадлежит мобильному оператору" in str(exc.value)


def test_validate_phone_number_empty():
    assert validate_phone_number("") is None


@pytest.mark.django_db
def test_validate_activation_token_valid(mocker, token):
    mocker.patch.object(token, "is_valid", return_value=True)

    validate_activation_token("12345678")


@pytest.mark.django_db
def test_validate_activation_token_expired(mocker, expired_token):
    mocker.patch.object(expired_token, "is_valid", return_value=False)

    with pytest.raises(ValidationError) as exc:
        validate_activation_token("12345678")

    assert "Срок действия ссылки истёк." in str(exc.value)
    assert not ActivationToken.objects.filter(token="12345678").exists()


@pytest.mark.django_db
def test_validate_activation_token_not_exists():
    with pytest.raises(ValidationError) as exc:
        validate_activation_token("not_exists")

    assert "Токен недействителен." in str(exc.value)
