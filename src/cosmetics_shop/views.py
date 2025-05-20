from django.shortcuts import render

from .models import Product, GroupProduct, Category


def index(request):
    return render(request, 'cosmetics_shop/index.html', {'title': 'Index'})


def main_page(request):
    group_product = GroupProduct.objects.all()
    product = Product.objects.all()
    return render(request, 'cosmetics_shop/main_page.html', {
        'title': 'Main page',
        'group_product': group_product,
        'product': product,
    })


def category_page(request):
    category = Category.objects.all()
    return render(request, 'cosmetics_shop/category_page.html', {
        'title': 'Category',
        'category': category,
    })


def product_page(request, product_id):
    product = Product.objects.get(id=product_id)
    return render(request, 'cosmetics_shop/product_page.html',
                  {
                      'title': 'Product',
                      'product_id': product_id,
                      'product': product,
                  })
