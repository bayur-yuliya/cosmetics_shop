from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from cosmetics_shop.models import Order, Product, Category


class Command(BaseCommand):
    help = "Создает стандартные группы с разрешениями для сотрудников"

    def handle(self, *args, **kwargs):
        sales_group, created = Group.objects.get_or_create(name="Менеджеры по продажам")
        sales_permissions = [
            "can_view_all_orders",
        ]

        order_content_type = ContentType.objects.get_for_model(Order)
        for perm_code in sales_permissions:
            perm = Permission.objects.get(
                content_type=order_content_type, codename=perm_code
            )
            sales_group.permissions.add(perm)

        content_group, created = Group.objects.get_or_create(name="Контент-менеджеры")
        content_permissions = [
            (Product, "can_edit_product"),
            (Product, "can_manage_product_stock"),
            (Category, "can_manage_categories"),
        ]

        for app_label, perm_code in content_permissions:
            content_type = ContentType.objects.get_for_model(app_label)
            perm = Permission.objects.get(content_type=content_type, codename=perm_code)
            content_group.permissions.add(perm)

        senior_group, created = Group.objects.get_or_create(name="Старшие менеджеры")
        all_order_perms = Permission.objects.filter(content_type=order_content_type)
        senior_group.permissions.add(*all_order_perms)

        self.stdout.write(self.style.SUCCESS("Группы успешно созданы!"))
