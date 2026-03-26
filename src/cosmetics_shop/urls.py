from django.urls import path

from . import ajax
from .views import cart, catalog, orders, static_pages

urlpatterns = [
    # ajax
    path(
        "ajax/favorites/",
        ajax.toggle_favorite,
        name="ajax_toggle_favorites",
    ),
    # ajax cart
    path("ajax/cart/add/", ajax.add_to_cart, name="ajax_add_to_cart"),
    path(
        "ajax/cart/remove/",
        ajax.cart_remove,
        name="ajax_cart_remove",
    ),
    # catalog
    path("groups/<slug:group_slug>/", catalog.group_page, name="group_page"),
    path(
        "categories/<slug:category_slug>/", catalog.category_page, name="category_page"
    ),
    path("products/<int:product_code>/", catalog.product_page, name="product_page"),
    path("brands/<slug:brand_slug>/", catalog.brand_products, name="brand_detail"),
    path("brands/", catalog.brand_page, name="brand_page"),
    # cart
    path("cart/<int:product_id>/delete/", cart.cart_delete, name="cart_delete"),
    path("cart/clean/", cart.clean_cart, name="clean_cart"),
    path("cart/", cart.cart, name="cart"),
    # order
    path("order/success/", orders.order_success, name="order_success"),
    path("order/", orders.create_order, name="order"),
    path("delivery/", orders.delivery, name="delivery"),
    # static_pages
    path(
        "payment_and_delivery/",
        static_pages.payment_and_delivery,
        name="payment_and_delivery",
    ),
    path("privacy-policy/", static_pages.privacy_policy, name="privacy_policy"),
    # main page
    path("", catalog.main_page, name="main_page"),
]
