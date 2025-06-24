from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render, redirect

from cosmetics_shop.models import Product
from stuff.forms import ProductForm


@staff_member_required
def index(request):
    title = 'Главная страница'
    return render(request, 'stuff/dashboard.html', {
        'title': title,
    })


@staff_member_required
def products(request):
    title = 'Товары'
    products = Product.objects.all().order_by('-id')
    return render(request, 'stuff/products.html', {
        'title': title,
        'products': products,

    })


@staff_member_required
def create_products(request):
    title = 'Создание карточки товара'
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            form.save()
    form = ProductForm()
    return render(request, 'stuff/create_product.html', {
        'title': title,
        'form': form,
    })


@staff_member_required
def edit_products(request, product_id):
    title = 'Изменение товара'
    product = Product.objects.get(id=product_id)
    if request.method == 'POST':
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            return redirect('products')
    form = ProductForm(instance=product)
    return render(request, 'stuff/edit_product.html', {
        'title': title,
        'form': form,
    })


@staff_member_required
def delete_products(request):
    pass


@staff_member_required
def orders(request):
    pass
