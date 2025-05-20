from django.urls import path
from . import views

urlpatterns = [
    path('category/', views.category_page, name='category_page'),
    path('main/', views.main_page, name='main_page'),
    path('product/<int:product_id>/', views.product_page, name='product_page'),
    path('', views.index, name='index'),
]
