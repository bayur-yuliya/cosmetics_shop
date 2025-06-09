from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect

from .models import Product, GroupProduct, Category, Brand


def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})


def main_page(request):
    category = Category.objects.all()
    group_product = GroupProduct.objects.all()
    product = Product.objects.all()
    return render(request, 'cosmetics_shop/main_page.html', {
        'title': 'Main page',
        'group_product': group_product,
        'product': product,
        'category': category,
    })


def category_page(request, category_id):
    category = Category.objects.filter(id=category_id)
    group_product = GroupProduct.objects.filter(category=category_id)
    product = Product.objects.filter(group__in=group_product)
    return render(request, 'cosmetics_shop/category_page.html', {
        'title': 'Category',
        'category': category,
        'group_product': group_product,
        'product': product,
    })


def group_page(request, group_id):
    group_product = GroupProduct.objects.filter(id=group_id)
    product = Product.objects.filter(group__in=group_product)
    return render(request, 'cosmetics_shop/category_page.html', {
        'title': 'Category',
        'group_product': group_product,
        'product': product,
    })


def product_page(request, product_id):
    product = Product.objects.get(id=product_id)
    return render(request, 'cosmetics_shop/product_page.html',
                  {
                      'title': 'Product',
                      'product_id': product_id,
                      'product': product,
                  })


def brand_page(request):
    brands = Brand.objects.all()
    return render(request, 'cosmetics_shop/brand.html',
                  {
                      'title': 'Brands',
                      'brands': brands,
                  })


def brand_products(request, brand_id):
    title = Brand.objects.get(id=brand_id)
    brand_products = Product.objects.filter(brand=brand_id)
    return render(request, 'cosmetics_shop/brand_products.html',
                  {
                      'title': title.name_brand,
                      'brand_products': brand_products,
                  })

