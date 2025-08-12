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
    # categories
    path("categories/create/", views.create_categories, name="create_categories"),
    path("categories/edit/<int:pk>/", views.edit_categories, name="edit_categories"),
    path("categories/delete/", views.delete_categories, name="delete_categories"),
    path("categories/", views.categories_list, name="categories_list"),
    # groups
    path("groups/create/", views.create_groups, name="create_groups"),
    path("groups/edit/<int:pk>/", views.edit_groups, name="edit_groups"),
    path("groups/delete/", views.delete_groups, name="delete_groups"),
    path("groups/", views.groups_list, name="groups_list"),
    # brands
    path("brands/create/", views.create_brands, name="create_brands"),
    path("brands/edit/<int:pk>/", views.edit_brands, name="edit_brands"),
    path("brands/delete/", views.delete_brands, name="delete_brands"),
    path("brands/", views.brands_list, name="brands_list"),
    # tags
    path("tags/create/", views.create_tags, name="create_tags"),
    path("tags/edit/<int:pk>/", views.edit_tags, name="edit_tags"),
    path("tags/delete/", views.delete_tags, name="delete_tags"),
    path("tags/", views.tags_list, name="tags_list"),
    path("", views.index, name="index"),
]
