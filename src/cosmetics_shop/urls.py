from django.urls import path
from . import views

urlpatterns = [
    path('group/<int:group_id>/', views.group_page, name='group_page'),
    path('category/<int:category_id>/', views.category_page, name='category_page'),
    path('product/<int:product_id>/', views.product_page, name='product_page'),
    path('brand/', views.brand_page, name='brand_page'),
    path('brand/<int:brand_id>', views.brand_products, name='brand_detail'),
    path('register/', views.register, name='register'),
    path('', views.main_page, name='main_page'),
]
