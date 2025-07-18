from django.urls import path

from stuff import views


urlpatterns = [
    path("products/edit/<int:product_id>", views.edit_products, name="edit_products"),
    path("products/create/", views.create_products, name="create_products"),
    path("products/", views.products, name="products"),
    path("product/<int:product_id>", views.product_card, name="product_card"),
    path("product/delete", views.delete_product, name="delete_product"),
    path("orders/<str:order_code>", views.order_info, name="order_info"),
    path("orders/", views.orders, name="orders"),
    path("", views.index, name="index"),
]
