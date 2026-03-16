import pytest
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.mark.django_db
def test_authenticate_success(backend, request_obj):
    user = User.objects.create_user(
        email="test@test.com",
        password="password123",
        is_active=True,
    )

    result = backend.authenticate(
        request_obj,
        email="test@test.com",
        password="password123",
    )

    assert result == user


@pytest.mark.django_db
def test_authenticate_wrong_password(backend, request_obj):
    User.objects.create_user(
        email="test@test.com",
        password="password123",
        is_active=True,
    )

    result = backend.authenticate(
        request_obj,
        email="test@test.com",
        password="wrong",
    )

    assert result is None


@pytest.mark.django_db
def test_authenticate_inactive_user(backend, request_obj):
    User.objects.create_user(
        email="test@test.com",
        password="password123",
        is_active=False,
    )

    result = backend.authenticate(
        request_obj,
        email="test@test.com",
        password="password123",
    )

    assert result is None


@pytest.mark.django_db
def test_get_user_success(backend):
    user = User.objects.create_user(
        email="test@test.com",
        password="password123",
    )

    result = backend.get_user(user.id)

    assert result == user


@pytest.mark.django_db
def test_get_user_not_found(backend):
    result = backend.get_user(9999)

    assert result is None
