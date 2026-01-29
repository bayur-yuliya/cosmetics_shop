from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.core.management import BaseCommand

from accounts.models import CustomUser
from staff.models import StaffPermission

User = get_user_model()


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        content_type = ContentType.objects.get_for_model(StaffPermission)
        perm = Permission.objects.get(
            content_type=content_type,
            codename="manage_permission",
        )

        # всем суперпользователям
        for user in CustomUser.objects.filter(is_superuser=True):
            user.user_permissions.add(perm)

        self.stdout.write(
            self.style.SUCCESS("Право manage_permissions выдано суперпользователям!")
        )
