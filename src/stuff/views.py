from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render

from cosmetics_shop.models import Product


@staff_member_required
def index(request):
    title = 'Главная страница'
    return render(request, 'stuff/dashboard.html', {
        'title': title,
    })


@staff_member_required
def products(request):
    title = 'Товары'
    products = Product.objects.all()
    return render(request, 'stuff/products.html', {
        'title': title,
        'products': products,

    })


@staff_member_required
def create_products(request):
    title = 'Создание карточки товара'
    return render(request, 'stuff/create_product.html', {
        'title': title,
    })


@staff_member_required
def edit_products(request):
    pass


@staff_member_required
def delete_products(request):
    pass


@staff_member_required
def orders(request):
    pass
