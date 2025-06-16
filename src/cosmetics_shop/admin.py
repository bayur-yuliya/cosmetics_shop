from django.contrib import admin

from cosmetics_shop.models import Category, GroupProduct, Product, Brand, Cart, CartItem, Order, OrderItem

admin.site.register(Category)
admin.site.register(GroupProduct)
admin.site.register(Product)
admin.site.register(Brand)
admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(Order)
admin.site.register(OrderItem)
