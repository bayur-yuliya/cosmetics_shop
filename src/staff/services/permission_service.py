from typing import Any

from django.db import transaction
from django.db.models import Q, QuerySet
from django.contrib.auth.models import Permission


def get_individually_assigned_permits() -> QuerySet[Permission]:
    # Разрешения, которые можно назначать индивидуально
    permissions = Permission.objects.exclude(
        Q(
            content_type__app_label__in=[
                "account",
                "accounts",
                "admin",
                "auth",
                "contenttypes",
                "sessions",
                "socialaccount",
                "sites",
            ]
        )
        | Q(
            content_type__model__in=[
                "client",
                "cartitem",
                "favorite",
                "deliveryaddress",
                "cart",
            ]
        )
    )
    return permissions


def get_permissions_by_app():
    permissions = get_individually_assigned_permits()

    permissions_by_app: dict[str, Any] = {}
    for perm in permissions:
        app_label = perm.content_type.app_label
        if app_label not in permissions_by_app:
            permissions_by_app[app_label] = []
        permissions_by_app[app_label].append(perm)

    return permissions_by_app


def set_user_permissions(user, selected_groups, selected_permissions) -> bool:
    try:
        with transaction.atomic():
            group_ids = [int(pk) for pk in selected_groups] if selected_groups else []
            perm_ids = [int(pk) for pk in selected_permissions] if selected_permissions else []

            user.groups.set(group_ids)
            user.user_permissions.set(perm_ids)
            return True
    except (ValueError, TypeError):
        return False
