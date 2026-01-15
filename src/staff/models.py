from django.db import models


class StaffPermission(models.Model):
    class Meta:
        permissions = [
            ("manage_permission", "Может управлять правами и группами"),
            ("view_dashboard", "Может просматривать статистику"),
            ("can_change_product_price", "Может изменять цену товара"),
            ("can_manage_product_stock", "Может управлять остатками товара"),
            ("can_change_order_status", "Может изменять статус заказа"),
        ]