from datetime import timedelta

import pytest
from django.test import RequestFactory
from django.utils import timezone

from accounts.authentication import EmailAuthBackend
from accounts.models import ActivationToken
from cosmetics_shop.tests.conftest import address, client_obj, user  # noqa


@pytest.fixture
def token(user):  # noqa: F811
    date = timezone.now() + timedelta(days=5, hours=3)
    return ActivationToken.objects.create(user=user, token="12345678", expires_at=date)


@pytest.fixture
def expired_token(user):  # noqa: F811
    date = timezone.now() - timedelta(days=5, hours=3)
    return ActivationToken.objects.create(user=user, token="12345678", expires_at=date)


@pytest.fixture
def backend():
    return EmailAuthBackend()


@pytest.fixture
def request_obj():
    return RequestFactory().get("/")
