import pytest
from django.contrib.auth.models import Permission

from staff.services.permission_service import (
    get_individually_assigned_permits,
    get_permissions_by_app,
    set_user_permissions,
)


@pytest.mark.django_db
def test_get_individually_assigned_permits():
    perms = get_individually_assigned_permits()

    for perm in perms:
        assert perm.content_type.app_label not in [
            "account",
            "accounts",
            "admin",
            "auth",
            "contenttypes",
            "sessions",
            "socialaccount",
            "sites",
        ]

        assert perm.content_type.model not in [
            "client",
            "cartitem",
            "favorite",
            "deliveryaddress",
            "cart",
        ]


@pytest.mark.django_db
def test_get_individually_assigned_permits_not_empty():
    perms = get_individually_assigned_permits()

    assert perms.exists()


@pytest.mark.django_db
def test_get_permissions_by_app_structure():
    result = get_permissions_by_app()

    assert isinstance(result, dict)

    for app_label, perms in result.items():
        assert isinstance(app_label, str)
        assert isinstance(perms, list)

        for perm in perms:
            assert perm.content_type.app_label == app_label


@pytest.mark.django_db
def test_get_permissions_by_app_grouping():
    result = get_permissions_by_app()

    for app_label, perms in result.items():
        for perm in perms:
            assert perm.content_type.app_label == app_label


@pytest.mark.django_db
def test_set_user_permissions_success(user, group_permissions):
    perm = Permission.objects.first()

    result = set_user_permissions(
        user,
        selected_groups=[group_permissions.id],
        selected_permissions=[perm.id],
    )

    user.refresh_from_db()

    assert result is True
    assert group_permissions in user.groups.all()
    assert perm in user.user_permissions.all()


@pytest.mark.django_db
def test_set_user_permissions_clear_permissions(user):
    result = set_user_permissions(user, [], [])

    user.refresh_from_db()

    assert result is True
    assert user.groups.count() == 0
    assert user.user_permissions.count() == 0


@pytest.mark.django_db
def test_set_user_permissions_invalid_data(user):
    result = set_user_permissions(
        user,
        selected_groups=["abc"],
        selected_permissions=["xyz"],
    )

    assert result is False
