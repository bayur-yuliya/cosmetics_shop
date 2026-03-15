from datetime import timedelta

import pytest
from django.utils import timezone

from accounts.models import ActivationToken
from cosmetics_shop.tests.conftest import user, client_obj, address  # noqa


@pytest.fixture
def token(user):  # noqa: F811
    date = timezone.now() + timedelta(days=5, hours=3)
    token = ActivationToken.objects.create(user=user, token="12345678", expires_at=date)
    return token
