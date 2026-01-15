from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from cosmetics_shop.models import Order, Product, Category, Tag, GroupProduct
from staff.models import StaffPermission


class Command(BaseCommand):
    help = "Создает стандартные группы с разрешениями для сотрудников"

    def handle(self, *args, **kwargs):
        # Менеджеры по продажам
        sales_group, _ = Group.objects.get_or_create(name="Менеджеры магазина")
        sales_permissions = [
            "can_view_all_orders",
        ]
        a = [
            (StaffPermission, "view_dashboard"),
            (Order, "view_order"),
            (Product, "view_product"),
            (Category, "view_category"),
            (Tag, "view_tag"),
            (GroupProduct, "view_groupproduct"),
        ]

        order_content_type = ContentType.objects.get_for_model(Order)
        for perm_code in sales_permissions:
            perm = Permission.objects.get(
                content_type=order_content_type, codename=perm_code
            )
            sales_group.permissions.add(perm)

        # Контент-менеджеры
        content_group, _ = Group.objects.get_or_create(name="Контент-менеджеры")
        content_permissions = [
            (Product, "add_product"),
            (Product, "change_product"),
            (Product, "view_product"),
            (Category, "add_category"),
            (Category, "change_category"),
            (Category, "view_category"),
            (Tag, "add_tag"),
            (Tag, "change_tag"),
            (Tag, "view_tag"),
            (GroupProduct, "add_groupproduct"),
            (GroupProduct, "change_groupproduct"),
            (GroupProduct, "view_groupproduct"),
            (StaffPermission, "can_manage_product_stock"),
            (StaffPermission, "can_change_product_price"),
            (StaffPermission, "view_dashboard"),
        ]

        for app_label, perm_code in content_permissions:
            content_type = ContentType.objects.get_for_model(app_label)
            perm = Permission.objects.get(content_type=content_type, codename=perm_code)
            content_group.permissions.add(perm)

        # Оператор заказов
        operator_group, _ = Group.objects.get_or_create(name="Оператор заказов")
        operator_permissions = [
            (Order, "view_order"),
            (StaffPermission, "can_change_order_status"),
        ]

        for app_label, perm_code in operator_permissions:
            content_type = ContentType.objects.get_for_model(app_label)
            perm = Permission.objects.get(content_type=content_type, codename=perm_code)
            operator_group.permissions.add(perm)

        # Старшие менеджеры

        senior_group, _ = Group.objects.get_or_create(name="Администратор")
        all_order_perms = Permission.objects.filter(content_type=order_content_type)
        dashboard_perm = Permission.objects.get(
            content_type=ContentType.objects.get_for_model(StaffPermission),
            codename="view_dashboard"
        )
        senior_group.permissions.add(*all_order_perms, dashboard_perm)

        self.stdout.write(self.style.SUCCESS("Группы успешно созданы!"))
