from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.db.models import Sum, F
from django.shortcuts import render, redirect
from django.views.decorators.http import require_POST

from .models import Product, GroupProduct, Category, Brand, Cart, CartItem, Order, OrderItem
from .services.cart_services import add_product_to_cart, remove_product_to_cart, delete_product_to_cart, \
    calculate_cart_total
from .services.order_service import create_order_from_cart


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
    products = Product.objects.filter(brand=brand_id)
    return render(request, 'cosmetics_shop/brand_products.html',
                  {
                      'title': title.name_brand,
                      'brand_products': products,
                  })


@login_required
def add_to_cart(request):
    product_id = request.POST.get('product_id')
    if not product_id:
        return redirect('main_page')

    add_product_to_cart(request.user, product_id=product_id)
    return redirect('main_page')


def cart(request):
    current_cart = Cart.objects.get(user=User.objects.get(username=request.user))
    cart_items = CartItem.objects.filter(cart=current_cart)
    total_price = calculate_cart_total(request.user)

    return render(request, 'cosmetics_shop/cart.html', {
        'title': 'Корзина',
        'cart_items': cart_items,
        'total_price': total_price,
    })


def create_order(request):
    order = create_order_from_cart(request.user)
    if order:
        return redirect('order_success', order_id=order.id)
    return redirect('cart')


def order_success(request, order_id):
    title = 'Обработка заказа'
    order = Order.objects.get(id=order_id)
    products = OrderItem.objects.filter(order=order)
    status = 'Заказ успешно обработан'
    return render(request, 'cosmetics_shop/order_success.html', {
        'title': title,
        'order': order,
        'products': products,
        'status': status,
    })


@require_POST
def cart_add(request):
    product_id = request.POST.get("product_id")
    add_product_to_cart(request.user, product_id)
    return redirect("cart")


@require_POST
def cart_remove(request):
    product_id = request.POST.get("product_id")
    remove_product_to_cart(request.user, product_id)
    return redirect("cart")


@require_POST
def cart_delete(request):
    product_id = request.POST.get("product_id")
    delete_product_to_cart(request.user, product_id)
    return redirect("cart")
