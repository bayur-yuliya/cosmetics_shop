import logging

from django.contrib import messages
from django.contrib.auth.decorators import permission_required
from django.contrib.auth.models import Group
from django.db.models import Count, QuerySet
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from accounts.models import CustomUser
from staff.forms import (
    AdminCreateUserForm,
    GroupForm,
)

from ..services.permission_service import (
    get_permissions_by_app,
    set_user_permissions,
)

logger = logging.getLogger(__name__)


@permission_required("staff.manage_permission", raise_exception=True)
def staff_group_list(request: HttpRequest) -> HttpResponse:
    logger.debug(f"Groups list opened: user_id={request.user.id}")

    groups: QuerySet[Group] = Group.objects.annotate(
        user_count=Count("user")
    ).prefetch_related("permissions")

    return render(
        request,
        "staff/permissions/groups_list.html",
        {"title": "Список групп разрешений", "groups": groups},
    )


@permission_required("staff.manage_permission", raise_exception=True)
def staff_group_edit(request: HttpRequest, pk: int) -> HttpResponse:
    logger.debug(f"Edit group page: group_id={pk}, user_id={request.user.id}")

    group: Group | None = get_object_or_404(Group, pk=pk)
    form = GroupForm(request.POST or None, instance=group)

    if request.method == "POST" and form.is_valid():
        logger.info(f"Group update attempt: group_id={pk}, user_id={request.user.id}")

        form.save()
        return redirect("staff_groups_list")

    return render(
        request,
        "staff/permissions/edit_groups.html",
        {
            "title": "Страница управления разрешениями",
            "group": group,
            "form": form,
        },
    )


@permission_required("staff.manage_permission", raise_exception=True)
def staff_list(request: HttpRequest) -> HttpResponse:
    logger.debug(f"Staff list opened: user_id={request.user.id}")

    staffs: QuerySet[CustomUser] = CustomUser.objects.filter(
        is_staff=True
    ).prefetch_related("groups", "user_permissions")

    return render(
        request,
        "staff/permissions/staff_list.html",
        {"title": "Страница сотрудников", "staffs": staffs},
    )


@permission_required("staff.manage_permission", raise_exception=True)
def edit_staff_permissions(request: HttpRequest, user_id: int) -> HttpResponse:
    logger.debug(
        f"Edit permissions page: target_user_id={user_id}, admin_id={request.user.id}"
    )

    user = get_object_or_404(CustomUser, pk=user_id)

    if request.method == "POST":
        logger.info(
            f"Permissions update attempt: target_user_id={user_id},"
            f" admin_id={request.user.id}"
        )

        groups = request.POST.getlist("groups")
        perms = request.POST.getlist("permissions")

        if set_user_permissions(user, groups, perms):
            messages.success(request, "Права успешно обновлены")
            logger.info(
                f"Permissions updated: target_user_id={user_id},"
                f" admin_id={request.user.id}"
            )
            return redirect("staff_list")
        else:
            logger.warning(f"Permissions update failed: target_user_id={user_id}")
            messages.error(request, "Ошибка при обновлении прав")

    all_groups = Group.objects.all()
    user_groups = user.groups.all()

    return render(
        request,
        "staff/permissions/edit_staff_permissions.html",
        {
            "user": user,
            "title": "Изменение разрешений",
            "all_groups": all_groups,
            "user_groups": user_groups,
            "permissions_by_app": get_permissions_by_app(),
            "user_permissions": user.user_permissions.all(),
        },
    )


@permission_required("staff.manage_permission", raise_exception=True)
def create_staff_user(request: HttpRequest) -> HttpResponse:
    logger.info(f"Create staff user attempt: admin_id={request.user.id}")

    if request.method == "POST":
        form = AdminCreateUserForm(request.POST)

        if form.is_valid():
            user = form.save()
            logger.info(f"Staff user created: user_id={user.id}")
            return redirect("main_page")
        else:
            logger.warning(f"Invalid staff creation form: errors={form.errors}")
            return redirect("main_page")

    form = AdminCreateUserForm()
    return render(
        request,
        "staff/create_staff_user.html",
        {"form": form, "title": "Отправка приглашения сотруднику"},
    )
