from django.db import models
from django.utils.translation import gettext_lazy as _


class StaffPermission(models.Model):
    class Meta:
        permissions = [
            ("manage_permission", "Может управлять правами и группами"),
            ("dashboard_view", "Может просматривать статистику"),
            ("staff_add", "Может добавлять сотрудников"),
            (
                "hard_delete_and_recovery_products",
                "Может окончательно удалять и восстанавливать товары",
            ),
        ]
        verbose_name = _("разрешения сотрудников")
        verbose_name_plural = _("Разрешения сотрудников")
