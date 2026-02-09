from django.urls import path

from . import ajax
from .views import catalog, static_pages, orders, cart

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
    path("group/<int:group_id>/", catalog.group_page, name="group_page"),
    path("category/<int:category_id>/", catalog.category_page, name="category_page"),
    path("product/<int:product_code>/", catalog.product_page, name="product_page"),
    path("brand/<int:brand_id>/", catalog.brand_products, name="brand_detail"),
    path("brand/", catalog.brand_page, name="brand_page"),
    # cart
    path("cart/delete/", cart.cart_delete, name="cart_delete"),
    path("cart/clean/", cart.clean_cart, name="clean_cart"),
    path("cart/", cart.cart, name="cart"),
    # order
    path("order/success/", orders.order_success, name="order_success"),
    path("order/<int:address_id>", orders.create_order, name="order"),
    path("delivery/", orders.delivery, name="delivery"),
    # static_pages
    path(
        "payment_and_delivery/",
        static_pages.payment_and_delivery,
        name="payment_and_delivery",
    ),
    # main page
    path("", catalog.main_page, name="main_page"),
]
