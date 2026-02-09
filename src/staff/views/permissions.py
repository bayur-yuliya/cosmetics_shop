from typing import Any

from django.contrib.auth.decorators import permission_required
from django.contrib.auth.models import Group
from django.db.models import Count, QuerySet
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404

from accounts.models import CustomUser

from staff.forms import (
    GroupForm,
    AdminCreateUserForm,
)

from ..services.permission_service import get_individually_assigned_permits


@permission_required("staff.manage_permission", raise_exception=True)
def staff_group_list(request: HttpRequest) -> HttpResponse:
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
    group: Group | None = get_object_or_404(Group, pk=pk)
    form = GroupForm(request.POST or None, instance=group)

    if request.method == "POST" and form.is_valid():
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
    user = get_object_or_404(CustomUser, pk=user_id)

    if request.method == "POST":
        selected_groups: list[str] | None = request.POST.getlist("groups")
        if selected_groups:
            selected_groups_id = [int(pk) for pk in selected_groups]
            user.groups.set(selected_groups_id)

        selected_permissions = request.POST.getlist("permissions")
        if selected_permissions:
            perms_id = [int(pk) for pk in selected_permissions]
            user.user_permissions.set(perms_id)
        return redirect("staff_list")

    all_groups = Group.objects.all()
    user_groups = user.groups.all()

    permissions = get_individually_assigned_permits()

    permissions_by_app: dict[str, Any] = {}
    for perm in permissions:
        app_label = perm.content_type.app_label
        if app_label not in permissions_by_app:
            permissions_by_app[app_label] = []
        permissions_by_app[app_label].append(perm)

    return render(
        request,
        "staff/permissions/edit_staff_permissions.html",
        {
            "user": user,
            "title": "Изменение разрешений",
            "all_groups": all_groups,
            "user_groups": user_groups,
            "permissions_by_app": permissions_by_app,
            "user_permissions": user.user_permissions.all(),
        },
    )


@permission_required("staff.manage_permission", raise_exception=True)
def create_staff_user(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        form = AdminCreateUserForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("main_page")
    form = AdminCreateUserForm()
    return render(
        request,
        "staff/create_staff_user.html",
        {"form": form, "title": "Отправка приглашения сотруднику"},
    )
