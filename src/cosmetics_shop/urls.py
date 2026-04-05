from django.urls import path

from . import ajax
from .views import cart, catalog, nova_poshta, orders, static_pages

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
    # nova_poshta
    path("api/np/cities/", nova_poshta.cities_view, name="api_np_cities"),
    path("api/np/warehouses/", nova_poshta.warehouses_view, name="api_np_warehouses"),
    # catalog
    path("groups/<slug:group_slug>/", catalog.group_page, name="group_page"),
    path(
        "categories/<slug:category_slug>/", catalog.category_page, name="category_page"
    ),
    path("products/<int:product_code>/", catalog.product_page, name="product_page"),
    path("brands/<slug:brand_slug>/", catalog.brand_products, name="brand_detail"),
    path("brands/", catalog.brand_page, name="brand_page"),
    # cart
    path("cart/<int:product_code>/delete/", cart.cart_delete, name="cart_delete"),
    path("cart/clean/", cart.clean_cart, name="clean_cart"),
    path("cart/", cart.cart, name="cart"),
    # order
    path("order/result/", orders.order_result, name="order_result"),
    path("order/", orders.create_order, name="order"),
    path("delivery/", orders.delivery, name="delivery"),
    # payment
    path("pay_order/<int:order_id>/", orders.pay_order, name="pay_order"),
    path("api/payment/webhook/", orders.mono_webhook, name="mono_webhook"),
    # static_pages
    path(
        "payment_and_delivery/",
        static_pages.payment_and_delivery,
        name="payment_and_delivery",
    ),
    path("privacy-policy/", static_pages.privacy_policy, name="privacy_policy"),
    path("returns/", static_pages.returns, name="returns"),
    # main page
    path("", catalog.main_page, name="main_page"),
]
