from django.urls import path

from staff import ajax
from staff.views import dashboard, catalog, permissions, products, orders

urlpatterns = [
    # product
    path(
        "products/<int:product_id>/edit/", products.edit_products, name="edit_products"
    ),
    path(
        "products/<int:product_id>/delete/",
        products.delete_product,
        name="delete_product",
    ),
    path("products/<int:product_id>/", products.product_card, name="product_card"),
    path("products/create/", products.create_products, name="create_products"),
    path("products/", products.products, name="products"),
    # staff permissions
    path(
        "staff_groups/<int:pk>/edit/",
        permissions.staff_group_edit,
        name="edit_staff_groups",
    ),
    path("staff_groups/", permissions.staff_group_list, name="staff_groups_list"),
    path(
        "staff_list/<int:user_id>/groups/edit",
        permissions.edit_staff_permissions,
        name="edit_staff_permissions",
    ),
    path("staff_list/", permissions.staff_list, name="staff_list"),
    path("create/", permissions.create_staff_user, name="create_staff_user"),
    # orders
    path("orders/<str:order_code>", orders.order_info, name="order_info"),
    path("orders/", orders.orders, name="orders"),
    # categories
    path(
        "categories/<int:pk>/edit/",
        catalog.CategoryChangeView.as_view(),
        name="edit_categories",
    ),
    path(
        "categories/<int:pk>/delete/",
        catalog.CategoryDeleteView.as_view(),
        name="delete_categories",
    ),
    path(
        "categories/create/",
        catalog.CategoryCreateView.as_view(),
        name="create_categories",
    ),
    path("categories/", catalog.CategoryListView.as_view(), name="categories_list"),
    # groups
    path(
        "groups/<int:pk>/edit/",
        catalog.GroupProductChangeView.as_view(),
        name="edit_groups",
    ),
    path(
        "groups/<int:pk>/delete/",
        catalog.GroupProductDeleteView.as_view(),
        name="delete_groups",
    ),
    path(
        "groups/create/",
        catalog.GroupProductCreateView.as_view(),
        name="create_groups",
    ),
    path("groups/", catalog.GroupProductListView.as_view(), name="groups_list"),
    # brands
    path(
        "brands/<int:pk>/edit/",
        catalog.BrandChangeView.as_view(),
        name="edit_brands",
    ),
    path(
        "brands/<int:pk>/delete/",
        catalog.BrandDeleteView.as_view(),
        name="delete_brands",
    ),
    path("brands/create/", catalog.BrandCreateView.as_view(), name="create_brands"),
    path("brands/", catalog.BrandListView.as_view(), name="brands_list"),
    # tags
    path("tags/<int:pk>/edit/", catalog.TagChangeView.as_view(), name="edit_tags"),
    path("tags/<int:pk>/delete/", catalog.TagDeleteView.as_view(), name="delete_tags"),
    path("tags/create/", catalog.TagCreateView.as_view(), name="create_tags"),
    path("tags/", catalog.TagListView.as_view(), name="tags_list"),
    # ajax chart
    path(
        "ajax/charts/sales/",
        ajax.sales_comparison_chart_for_the_year,
        name="sales_data",
    ),
    # main page, dashboard
    path("", dashboard.index, name="index"),
]
