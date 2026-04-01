import logging
from typing import Any

from django.contrib.auth.models import Permission
from django.core.cache import cache
from django.db import transaction
from django.db.models import Q, QuerySet

logger = logging.getLogger(__name__)


def get_individually_assigned_permits() -> QuerySet[Permission]:
    # Разрешения, которые можно назначать индивидуально

    logger.debug("Fetching individually assignable permissions")

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


def get_permissions_by_app() -> dict[str, Any]:
    logger.debug("Grouping permissions by app")

    cache_key = "permissions_by_app"

    data = cache.get(cache_key)
    if data:
        return data

    permissions = get_individually_assigned_permits()

    permissions_by_app: dict[str, Any] = {}
    for perm in permissions:
        app_label = perm.content_type.app_label
        if app_label not in permissions_by_app:
            permissions_by_app[app_label] = []
        permissions_by_app[app_label].append(perm)

    logger.info(f"Permissions grouped: apps={len(permissions_by_app)}")

    cache.set(cache_key, permissions_by_app, timeout=60 * 60)  # 1 hour

    return permissions_by_app


def set_user_permissions(user, selected_groups, selected_permissions) -> bool:
    logger.info(f"Setting permissions: user_id={user.id}")

    try:
        with transaction.atomic():
            group_ids = [int(pk) for pk in selected_groups] if selected_groups else []
            perm_ids = (
                [int(pk) for pk in selected_permissions] if selected_permissions else []
            )

            user.groups.set(group_ids)
            user.user_permissions.set(perm_ids)

            logger.info(
                f"Permissions updated: user_id={user.id}, "
                f"groups={len(group_ids)}, perms={len(perm_ids)}"
            )

            return True
    except (ValueError, TypeError) as e:
        logger.warning(f"Invalid permissions data: user_id={user.id}, error={str(e)}")
        return False

    except Exception as e:
        logger.exception(
            f"Failed to set permissions: user_id={user.id}, error={str(e)}"
        )
        return False
