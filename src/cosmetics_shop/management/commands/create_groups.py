from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from cosmetics_shop.models import Order


class Command(BaseCommand):
    help = 'Создает стандартные группы с разрешениями для сотрудников'

    def handle(self, *args, **kwargs):
        sales_group, created = Group.objects.get_or_create(name='Менеджеры по продажам')
        sales_permissions = [
            'can_change_order_status',
            'can_view_all_orders',
            'can_export_orders',
        ]

        order_content_type = ContentType.objects.get_for_model(Order)
        for perm_code in sales_permissions:
            perm = Permission.objects.get(content_type=order_content_type, codename=perm_code)
            sales_group.permissions.add(perm)

        content_group, created = Group.objects.get_or_create(name='Контент-менеджеры')
        content_permissions = [
            ('product', 'can_edit_product_price'),
            ('product', 'can_manage_product_stock'),
            ('category', 'can_manage_categories'),
        ]

        for app_label, perm_code in content_permissions:
            perm = Permission.objects.get(content_type__app_label=app_label, codename=perm_code)
            content_group.permissions.add(perm)

        courier_group, created = Group.objects.get_or_create(name='Курьеры')
        courier_permissions = [
            ('order', 'can_change_order_status'),
        ]

        for app_label, perm_code in courier_permissions:
            perm = Permission.objects.get(content_type__app_label=app_label, codename=perm_code)
            courier_group.permissions.add(perm)

        senior_group, created = Group.objects.get_or_create(name='Старшие менеджеры')
        all_order_perms = Permission.objects.filter(content_type=order_content_type)
        senior_group.permissions.add(*all_order_perms)

        self.stdout.write(self.style.SUCCESS('Группы успешно созданы!'))