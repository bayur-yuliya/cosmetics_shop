from django.urls import path

from stuff import views


urlpatterns = [
    path("products/edit/<int:product_id>", views.edit_products, name="edit_products"),
    path("products/create/", views.create_products, name="create_products"),
    path("products/<int:product_id>", views.product_card, name="product_card"),
    path("products/delete", views.delete_product, name="delete_product"),
    path("products/", views.products, name="products"),
    path("orders/<str:order_code>", views.order_info, name="order_info"),
    path("orders/", views.orders, name="orders"),
    path("categories/create/", views.create_categories, name="create_categories"),
    path("categories/", views.categories_list, name="categories_list"),
    path("groups/create/", views.create_groups, name="create_groups"),
    path("groups/", views.groups_list, name="groups_list"),
    path("brands/create/", views.create_brands, name="create_brands"),
    path("brands/", views.brands_list, name="brands_list"),
    path("tags/create/", views.create_tags, name="create_tags"),
    path("tags/", views.tags_list, name="tags_list"),
    path("", views.index, name="index"),
]
