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
