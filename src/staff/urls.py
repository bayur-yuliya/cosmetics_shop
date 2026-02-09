from django.urls import path

from staff import ajax
from staff.views import dashboard, directories, permissions, products, orders

urlpatterns = [
    # product
    path("products/edit/<int:product_id>", products.edit_products, name="edit_products"),
    path("products/create/", products.create_products, name="create_products"),
    path("products/<int:product_id>", products.product_card, name="product_card"),
    path("products/delete", products.delete_product, name="delete_product"),
    path("products/", products.products, name="products"),

    # staff permissions
    path("create/", permissions.create_staff_user, name="create_staff_user"),
    path(
        "staff_groups/edit/<int:pk>/", permissions.staff_group_edit, name="edit_staff_groups"
    ),
    path("staff_groups/", permissions.staff_group_list, name="staff_groups_list"),
    path(
        "staff_list/<int:user_id>/groups/edit",
        permissions.edit_staff_permissions,
        name="edit_staff_permissions",
    ),
    path("staff_list/", permissions.staff_list, name="staff_list"),
    # orders
    path("orders/<str:order_code>", orders.order_info, name="order_info"),
    path("orders/", orders.orders, name="orders"),
    # categories
    path(
        "categories/create/",
        directories.CategoryCreateView.as_view(),
        name="create_categories",
    ),
    path(
        "categories/edit/<int:pk>/",
        directories.CategoryChangeView.as_view(),
        name="edit_categories",
    ),
    path(
        "categories/delete/<int:pk>/",
        directories.CategoryDeleteView.as_view(),
        name="delete_categories",
    ),
    path("categories/", directories.CategoryListView.as_view(), name="categories_list"),
    # groups
    path(
        "groups/create/", directories.GroupProductCreateView.as_view(), name="create_groups"
    ),
    path(
        "groups/edit/<int:pk>/",
        directories.GroupProductChangeView.as_view(),
        name="edit_groups",
    ),
    path(
        "groups/delete/<int:pk>/",
        directories.GroupProductDeleteView.as_view(),
        name="delete_groups",
    ),
    path("groups/", directories.GroupProductListView.as_view(), name="groups_list"),
    # brands
    path("brands/create/", directories.BrandCreateView.as_view(), name="create_brands"),
    path("brands/edit/<int:pk>/", directories.BrandChangeView.as_view(), name="edit_brands"),
    path(
        "brands/delete/<int:pk>/", directories.BrandDeleteView.as_view(), name="delete_brands"
    ),
    path("brands/", directories.BrandListView.as_view(), name="brands_list"),
    # tags
    path("tags/create/", directories.TagCreateView.as_view(), name="create_tags"),
    path("tags/edit/<int:pk>/", directories.TagChangeView.as_view(), name="edit_tags"),
    path("tags/delete/<int:pk>/", directories.TagDeleteView.as_view(), name="delete_tags"),
    path("tags/", directories.TagListView.as_view(), name="tags_list"),
    # chart
    path(
        "ajax/charts/sales/",
        ajax.sales_comparison_chart_for_the_year,
        name="sales_data",
    ),
    # main page, dashboard
    path("", dashboard.index, name="index"),
]
