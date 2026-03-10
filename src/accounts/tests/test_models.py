from datetime import timedelta

import pytest
from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.utils import timezone

from accounts.models import ActivationToken


User = get_user_model()


# CustomUserManager tests
@pytest.mark.django_db
def test_create_user_success():
    user = User.objects.create_user(email="user@test.com", password="password")

    assert user.email == "user@test.com"
    assert user.check_password("password")
    assert user.is_staff is False
    assert user.is_superuser is False


@pytest.mark.django_db
def test_create_superuser_without_staff():
    with pytest.raises(ValueError, match="Superuser must have is_staff=True."):
        User.objects.create_superuser(
            email="user@test.com", password="password", is_staff=False
        )


@pytest.mark.django_db
def test_create_superuser_without_is_superuser():
    with pytest.raises(ValueError, match="Superuser must have is_superuser=True."):
        User.objects.create_superuser(
            email="user@test.com", password="password", is_superuser=False
        )


@pytest.mark.django_db
def test_create_user_without_email():
    with pytest.raises(ValueError):
        User.objects.create_user(email=None, password="123")


@pytest.mark.django_db
def test_create_superuser():
    admin = User.objects.create_superuser(email="admin@test.com", password="adminpass")

    assert admin.is_staff is True
    assert admin.is_superuser is True


@pytest.mark.django_db
def test_user_str():
    user = User.objects.create_user(email="user@test.com", password="123")
    assert str(user) == "user@test.com"


# CustomUser model
@pytest.mark.django_db
def test_email_unique():
    User.objects.create_user(email="user@test.com", password="123")

    with pytest.raises(IntegrityError):
        User.objects.create_user(email="user@test.com", password="123")


# ActivationToken
@pytest.mark.django_db
def test_create_activation_token():
    user = User.objects.create_user(email="user@test.com", password="123")

    token = ActivationToken.create_for_user(user)

    assert token.user == user
    assert token.token is not None
    assert token.expires_at > timezone.now()


@pytest.mark.django_db
def test_token_is_valid_true():
    user = User.objects.create_user(email="user@test.com", password="123")

    token = ActivationToken.create_for_user(user)

    assert token.is_valid() is True


@pytest.mark.django_db
def test_token_is_valid_false():
    user = User.objects.create_user(email="user@test.com", password="123")

    token = ActivationToken.objects.create(
        user=user,
        token="testtoken",
        expires_at=timezone.now() - timedelta(hours=1),
    )

    assert token.is_valid() is False


@pytest.mark.django_db
def test_only_one_token_per_user():
    user = User.objects.create_user(email="user@test.com", password="123")

    ActivationToken.create_for_user(user)

    with pytest.raises(Exception):
        ActivationToken.create_for_user(user)
