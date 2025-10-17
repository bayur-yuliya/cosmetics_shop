from django.urls import path
from . import views

urlpatterns = [
    path("account/login/", views.login_view, name="account_login"),
    path("group/<int:group_id>/", views.group_page, name="group_page"),
    path("category/<int:category_id>/", views.category_page, name="category_page"),
    path("product/<int:product_code>/", views.product_page, name="product_page"),
    path("brand/", views.brand_page, name="brand_page"),
    path("brand/<int:brand_id>/", views.brand_products, name="brand_detail"),
    path("add_to_cart/", views.add_to_cart, name="add_to_cart"),
    path("cart/add/", views.cart_add, name="cart_add"),
    path("cart/remove/", views.cart_remove, name="cart_remove"),
    path("cart/delete/", views.cart_delete, name="cart_delete"),
    path("cart/", views.cart, name="cart"),
    path("order_history/", views.order_history, name="order_history"),
    path("order_success/<int:order_id>/", views.order_success, name="order_success"),
    path("order/<int:address_id>", views.create_order, name="order"),
    path("user_account/contact/", views.user_contact, name="user_contact"),
    path("user_account/", views.user_account, name="user_account"),
    path("delete_account/", views.delete_account, name="delete_account"),
    path("delivery/", views.delivery, name="delivery"),
    path("logout/", views.logout_view, name="logout"),
    path("favorites/", views.favorites, name="favorites"),
    path(
        "payment_and_delivery/", views.payment_and_delivery, name="payment_and_delivery"
    ),
    path(
        "favorites/add/<int:product_id>/",
        views.add_to_favorites,
        name="add_to_favorites",
    ),
    path(
        "favorites/remove/<int:product_id>/",
        views.remove_from_favorites,
        name="remove_from_favorites",
    ),
    path("", views.main_page, name="main_page"),
]
