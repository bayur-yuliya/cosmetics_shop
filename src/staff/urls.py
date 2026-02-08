from django.urls import path

from staff import views, ajax

urlpatterns = [
    path("create/", views.create_staff_user, name="create_staff_user"),
    path("products/edit/<int:product_id>", views.edit_products, name="edit_products"),
    path("products/create/", views.create_products, name="create_products"),
    path("products/<int:product_id>", views.product_card, name="product_card"),
    path("products/delete", views.delete_product, name="delete_product"),
    path("products/", views.products, name="products"),
    # staff permissions
    path(
        "staff_groups/edit/<int:pk>/", views.staff_group_edit, name="edit_staff_groups"
    ),
    path("staff_groups/", views.staff_group_list, name="staff_groups_list"),
    path(
        "staff_list/<int:user_id>/groups/edit",
        views.edit_staff_permissions,
        name="edit_staff_permissions",
    ),
    path("staff_list/", views.staff_list, name="staff_list"),
    # orders
    path("orders/<str:order_code>", views.order_info, name="order_info"),
    path("orders/", views.orders, name="orders"),
    # categories
    path(
        "categories/create/",
        views.CategoryCreateView.as_view(),
        name="create_categories",
    ),
    path(
        "categories/edit/<int:pk>/",
        views.CategoryChangeView.as_view(),
        name="edit_categories",
    ),
    path(
        "categories/delete/<int:pk>/",
        views.CategoryDeleteView.as_view(),
        name="delete_categories",
    ),
    path("categories/", views.CategoryListView.as_view(), name="categories_list"),
    # groups
    path(
        "groups/create/", views.GroupProductCreateView.as_view(), name="create_groups"
    ),
    path(
        "groups/edit/<int:pk>/",
        views.GroupProductChangeView.as_view(),
        name="edit_groups",
    ),
    path(
        "groups/delete/<int:pk>/",
        views.GroupProductDeleteView.as_view(),
        name="delete_groups",
    ),
    path("groups/", views.GroupProductListView.as_view(), name="groups_list"),
    # brands
    path("brands/create/", views.BrandCreateView.as_view(), name="create_brands"),
    path("brands/edit/<int:pk>/", views.BrandChangeView.as_view(), name="edit_brands"),
    path(
        "brands/delete/<int:pk>/", views.BrandDeleteView.as_view(), name="delete_brands"
    ),
    path("brands/", views.BrandListView.as_view(), name="brands_list"),
    # tags
    path("tags/create/", views.TagCreateView.as_view(), name="create_tags"),
    path("tags/edit/<int:pk>/", views.TagChangeView.as_view(), name="edit_tags"),
    path("tags/delete/<int:pk>/", views.TagDeleteView.as_view(), name="delete_tags"),
    path("tags/", views.TagListView.as_view(), name="tags_list"),
    # chart
    path(
        "ajax/charts/sales/",
        ajax.sales_comparison_chart_for_the_year,
        name="sales_data",
    ),
    # main page
    path("", views.index, name="index"),
]
