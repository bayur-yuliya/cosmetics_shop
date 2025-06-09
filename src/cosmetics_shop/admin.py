from django.contrib import admin

from cosmetics_shop.models import Category, GroupProduct, Product, Brand, Card, CardItem, Order, OrderItem

admin.site.register(Category)
admin.site.register(GroupProduct)
admin.site.register(Product)
admin.site.register(Brand)
admin.site.register(Card)
admin.site.register(CardItem)
admin.site.register(Order)
admin.site.register(OrderItem)
