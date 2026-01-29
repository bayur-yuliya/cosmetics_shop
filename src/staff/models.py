from django.db import models
from django.utils.translation import gettext_lazy as _


class StaffPermission(models.Model):
    class Meta:
        permissions = [
            ("manage_permission", "Может управлять правами и группами"),
            ("view_dashboard", "Может просматривать статистику"),
            ("add_staff", "Может добавлять сотрудников"),
        ]
        verbose_name = _("Разрешения сотрудника")
        verbose_name_plural = _("Разрешения сотрудников")
