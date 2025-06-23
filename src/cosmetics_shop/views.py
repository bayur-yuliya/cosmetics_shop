import uuid

from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.db import transaction
from django.shortcuts import render, redirect
from django.views.decorators.http import require_POST

from .forms import ClientForm, DeliveryAddressForm
from .models import Product, GroupProduct, Category, Brand, CartItem, Order, OrderItem, Client
from .services.cart_services import add_product_to_cart, \
    get_or_create_cart_for_session, get_or_create_cart, \
    remove_product_from_cart, delete_product_from_cart, get_or_create_session_client
from .services.order_service import create_order_from_cart, get_client


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


@login_required
def logout_view(request):
    logout(request)
    return redirect('main_page')


@login_required
@transaction.atomic
def delete_account(request):
    user = request.user

    user.username = f'deleted_user_{uuid.uuid4().hex[:8]}'
    user.email = ''
    user.first_name = ''
    user.last_name = ''

    user.is_active = False
    user.save()

    logout(request)

    return redirect('main_page')


@login_required
def user_account(request):
    title = 'Аккаунт'
    return render(request, 'cosmetics_shop/user_account.html', {
        'title': title,
    })


@login_required
def order_history(request):
    title = 'История заказов'
    orders = Order.objects.filter(client=Client.objects.get(user=request.user))
    return render(request, 'cosmetics_shop/order_history.html', {
        'title': title,
        'orders': orders,
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


def add_to_cart(request):
    product_id = request.POST.get('product_id')
    if not product_id:
        return redirect('main_page')

    if request.user.is_authenticated:
        add_product_to_cart(request, product_id=product_id)

    else:
        cart = get_or_create_cart_for_session(request)
        product = Product.objects.get(id=product_id)

        item, created = CartItem.objects.get_or_create(cart=cart, product=product)

        item.quantity += 1
        item.save()
    return redirect('main_page')


def cart(request):
    current_cart = get_or_create_cart(request)
    cart_items = CartItem.objects.select_related('product').filter(cart=current_cart)
    total_price = sum(item.product.price * item.quantity for item in cart_items)

    return render(request, 'cosmetics_shop/cart.html', {
        'title': 'Корзина',
        'cart_items': cart_items,
        'total_price': total_price,
    })


def create_order(request, address_id):
    order = create_order_from_cart(request, address_id)
    if order:
        return redirect('order_success', order_id=order.id)
    return redirect('delivery')


def order_success(request, order_id):
    title = 'Заказ'
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
    add_product_to_cart(request, product_id)
    return redirect("cart")


@require_POST
def cart_remove(request):
    product_id = request.POST.get("product_id")
    remove_product_from_cart(request, product_id)
    return redirect("cart")


@require_POST
def cart_delete(request):
    product_id = request.POST.get("product_id")
    delete_product_from_cart(request, product_id)
    return redirect("cart")


def delivery(request):
    title = 'Оформление заказа'

    if request.method == 'POST':
        form = ClientForm(request.POST)
        form_delivery = DeliveryAddressForm(request.POST)

        if form.is_valid() and form_delivery.is_valid():
            if request.user.is_authenticated:
                client, _ = Client.objects.get_or_create(user=request.user)
                client.full_name = form.cleaned_data['full_name']
                client.email = form.cleaned_data['email']
                client.phone = form.cleaned_data['phone']
                client.is_active = True
                client.save()
            else:
                client = get_or_create_session_client(request, form)

            address = form_delivery.save(commit=False)
            address.client = client
            address.save()

            return redirect('order', address_id=address.id)

    else:
        try:
            client = get_client(request)
            form = ClientForm(instance=client)
        except Client.DoesNotExist:
            form = ClientForm()

        form_delivery = DeliveryAddressForm()

    return render(request, 'cosmetics_shop/delivery.html', {
        'title': title,
        'form': form,
        'form_delivery': form_delivery,
    })
