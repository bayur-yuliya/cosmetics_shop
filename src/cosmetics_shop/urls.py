from django.urls import path
from . import views

urlpatterns = [
    path('group/<int:group_id>/', views.group_page, name='group_page'),
    path('category/<int:category_id>/', views.category_page, name='category_page'),
    path('product/<int:product_id>/', views.product_page, name='product_page'),
    path('brand/', views.brand_page, name='brand_page'),
    path('brand/<int:brand_id>/', views.brand_products, name='brand_detail'),
    path('register/', views.register, name='register'),
    path('add_to_card/', views.add_to_card, name="add_to_cart"),
    path("cart/add/", views.cart_add, name="cart_add"),
    path("cart/remove/", views.cart_remove, name="cart_remove"),
    path("cart/delete/", views.cart_delete, name="cart_delete"),
    path('card/', views.card, name='card'),
    path('order_success/<int:order_id>/', views.order_success, name='order_success'),
    path('order/', views.create_order, name='order'),
    path('', views.main_page, name='main_page'),
]
