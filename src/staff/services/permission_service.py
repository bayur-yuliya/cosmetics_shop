from django.db.models import Q
from django.contrib.auth.models import Permission


def get_individually_assigned_permits():
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


def get_individually_assigned_permits_names():
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
    ).values_list("name", flat=True)
    return permissions
