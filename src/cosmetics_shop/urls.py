from django.urls import path
from . import views, ajax

urlpatterns = [
    # ajax
    path(
        "ajax/favorites/add/<int:product_id>/",
        ajax.toggle_favorite,
        name="ajax_add_to_favorites",
    ),
    path(
        "ajax/favorites/delete/<int:product_id>/",
        ajax.toggle_favorite,
        name="ajax_remove_to_favorites",
    ),
    path(
        "ajax/cart/add/<int:product_code>/", ajax.add_to_cart, name="ajax_add_to_cart"
    ),
    # login
    path("account/login/", views.login_view, name="account_login"),
    path("group/<int:group_id>/", views.group_page, name="group_page"),
    path("category/<int:category_id>/", views.category_page, name="category_page"),
    path("product/<int:product_code>/", views.product_page, name="product_page"),
    path("brand/", views.brand_page, name="brand_page"),
    path("brand/<int:brand_id>/", views.brand_products, name="brand_detail"),
    path("add_to_cart/", views.add_to_cart, name="add_to_cart"),
    # cart
    path("cart/remove/", views.cart_remove, name="cart_remove"),
    path("cart/delete/", views.cart_delete, name="cart_delete"),
    path("cart/", views.cart, name="cart"),
    # order
    path("order_success/", views.order_success, name="order_success"),
    path("order/<int:address_id>", views.create_order, name="order"),
    path("delivery/", views.delivery, name="delivery"),
    path(
        "payment_and_delivery/", views.payment_and_delivery, name="payment_and_delivery"
    ),
    path("", views.main_page, name="main_page"),
]
