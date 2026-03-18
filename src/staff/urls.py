from django.urls import path

from staff import ajax
from staff.views import catalog, dashboard, orders, permissions, products

urlpatterns = [
    # products
    path("products/", products.products, name="products"),
    path("products/create/", products.create_products, name="create_products"),
    path("products/<int:product_code>/", products.product_card, name="product_card"),
    path(
        "products/<int:product_code>/edit/",
        products.edit_products,
        name="edit_products",
    ),
    path(
        "products/<int:product_id>/delete/",
        products.delete_product,
        name="delete_product",
    ),
    # staff permissions
    path(
        "staff_groups/<int:pk>/edit/",
        permissions.staff_group_edit,
        name="edit_staff_groups",
    ),
    path("staff_groups/", permissions.staff_group_list, name="staff_groups_list"),
    path(
        "staff_list/<int:user_id>/groups/edit/",
        permissions.edit_staff_permissions,
        name="edit_staff_permissions",
    ),
    path("staff_list/", permissions.staff_list, name="staff_list"),
    path("create/", permissions.create_staff_user, name="create_staff_user"),
    # orders
    path("orders/", orders.orders, name="orders"),
    path("orders/<str:order_code>/", orders.order_info, name="order_info"),
    # categories
    path("categories/", catalog.CategoryListView.as_view(), name="categories_list"),
    path(
        "categories/create/",
        catalog.CategoryCreateView.as_view(),
        name="create_categories",
    ),
    path(
        "categories/<slug:slug>/edit/",
        catalog.CategoryChangeView.as_view(),
        name="edit_categories",
    ),
    path(
        "categories/<int:pk>/delete/",
        catalog.CategoryDeleteView.as_view(),
        name="delete_categories",
    ),
    # groups
    path("groups/", catalog.GroupProductListView.as_view(), name="groups_list"),
    path(
        "groups/create/",
        catalog.GroupProductCreateView.as_view(),
        name="create_groups",
    ),
    path(
        "groups/<slug:slug>/edit/",
        catalog.GroupProductChangeView.as_view(),
        name="edit_groups",
    ),
    path(
        "groups/<int:pk>/delete/",
        catalog.GroupProductDeleteView.as_view(),
        name="delete_groups",
    ),
    # brands
    path("brands/", catalog.BrandListView.as_view(), name="brands_list"),
    path("brands/create/", catalog.BrandCreateView.as_view(), name="create_brands"),
    path(
        "brands/<slug:slug>/edit/",
        catalog.BrandChangeView.as_view(),
        name="edit_brands",
    ),
    path(
        "brands/<int:pk>/delete/",
        catalog.BrandDeleteView.as_view(),
        name="delete_brands",
    ),
    # tags
    path("tags/", catalog.TagListView.as_view(), name="tags_list"),
    path("tags/create/", catalog.TagCreateView.as_view(), name="create_tags"),
    path("tags/<int:pk>/edit/", catalog.TagChangeView.as_view(), name="edit_tags"),
    path("tags/<int:pk>/delete/", catalog.TagDeleteView.as_view(), name="delete_tags"),
    # ajax chart
    path(
        "ajax/charts/sales/",
        ajax.sales_comparison_chart_for_the_year,
        name="sales_data",
    ),
    # main page, dashboard
    path("", dashboard.index, name="index"),
]
