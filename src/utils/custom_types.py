from typing import TypeGuard
from django.contrib.auth.models import AnonymousUser
from django.http import HttpRequest

from accounts.models import CustomUser


class AuthenticatedRequest(HttpRequest):
    user: CustomUser


def is_fully_authenticated(user: CustomUser | AnonymousUser) -> TypeGuard[CustomUser]:
    return user.is_authenticated
