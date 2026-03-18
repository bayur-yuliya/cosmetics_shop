from unittest.mock import patch

import pytest

from accounts.forms import ClientCreationForm, SetInitialPasswordForm
from cosmetics_shop.models import Client


@pytest.mark.django_db
def test_client_creation_form_valid():
    form = ClientCreationForm(
        data={
            "first_name": "Test first name",
            "last_name": "Test last name",
            "email": "test@test.com",
            "phone": "+380671234567",
        }
    )
    assert form.is_valid()


@pytest.mark.django_db
def test_client_creation_form_invalid_phone():
    form = ClientCreationForm(
        data={
            "first_name": "Test first name",
            "last_name": "Test last name",
            "email": "test@test.com",
            "phone": "123",
        }
    )

    assert not form.is_valid()
    assert "phone" in form.errors


@pytest.mark.django_db
def test_client_creation_form_save_when_changed():
    form = ClientCreationForm(
        data={
            "first_name": "Test first name",
            "last_name": "Test last name",
            "email": "test@test.com",
            "phone": "+380501234567",
        }
    )

    assert form.is_valid()

    instance = form.save()

    assert Client.objects.count() == 1
    assert instance.first_name == "Test first name"
    assert instance.last_name == "Test last name"
    assert instance.email == "test@test.com"
    assert instance.phone == "+380501234567"


@pytest.mark.django_db
def test_client_creation_form_not_saved_if_not_changed():
    client = Client.objects.create(
        first_name="Test first name",
        last_name="Test last name",
        email="test@test.com",
        phone="+380501234567",
    )

    form = ClientCreationForm(
        data={
            "first_name": "Test first name",
            "last_name": "Test last name",
            "email": "test@test.com",
            "phone": "+380501234567",
        },
        instance=client,
    )

    assert form.is_valid()

    instance = form.save()

    assert Client.objects.count() == 1
    assert instance.pk == client.pk


def test_password_form_valid():
    form = SetInitialPasswordForm(
        data={
            "password1": "12345678",
            "password2": "12345678",
        }
    )

    assert form.is_valid()


def test_password_form_password_mismatch():
    form = SetInitialPasswordForm(
        data={
            "password1": "12345678",
            "password2": "87654321",
        }
    )

    assert not form.is_valid()
    assert "__all__" in form.errors


def test_get_user_and_password_called():
    form = SetInitialPasswordForm(
        data={
            "password1": "12345678",
            "password2": "12345678",
        },
        token="test-token",
    )

    assert form.is_valid()

    with patch("accounts.forms.activate_user") as mock_activate:
        mock_activate.return_value = "user_obj"

        user, password = form.get_user_and_password()

        mock_activate.assert_called_once_with("test-token", "12345678")
        assert user == "user_obj"
        assert password == "12345678"


def test_get_user_and_password_no_token():
    form = SetInitialPasswordForm(
        data={
            "password1": "12345678",
            "password2": "12345678",
        }
    )

    assert form.is_valid()

    result = form.get_user_and_password()

    assert result is None
