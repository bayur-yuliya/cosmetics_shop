from django.shortcuts import render

from .models import Product, GroupProduct, Category


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
    product = Product.objects.filter(group_product__in=group_product)
    return render(request, 'cosmetics_shop/category_page.html', {
        'title': 'Category',
        'category': category,
        'group_product': group_product,
        'product': product,
    })


def group_page(request, group_id):
    group_product = GroupProduct.objects.filter(id=group_id)
    product = Product.objects.filter(group_product__in=group_product)
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
