import uuid

from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.db import transaction
from django.shortcuts import render, redirect
from django.views.decorators.http import require_POST

from .forms import ClientForm, DeliveryAddressForm, ProductFilterForm
from .models import (
    Product,
    GroupProduct,
    Brand,
    CartItem,
    Order,
    OrderItem,
    Client,
    DeliveryAddress,
)
from .services.cart_services import (
    add_product_to_cart,
    get_or_create_cart_for_session,
    get_or_create_cart,
    remove_product_from_cart,
    delete_product_from_cart,
    get_or_create_session_client,
)
from .services.order_service import create_order_from_cart, get_client


def register(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("login")
    form = UserCreationForm()
    return render(request, "registration/register.html", {"form": form})


def main_page(request):
    group_product = GroupProduct.objects.all()
    products = Product.objects.all().order_by("-stock")
    cart = get_or_create_cart(request)
    cart_items = CartItem.objects.filter(cart=cart)
    count_cart_items = sum(item.quantity for item in cart_items)

    form = ProductFilterForm(request.GET or None)

    if form.is_valid():
        name = form.cleaned_data["name"]
        group = form.cleaned_data["group"]
        min_price = form.cleaned_data["min_price"]
        max_price = form.cleaned_data["max_price"]
        brand = form.cleaned_data["brand"]

        if min_price is not None:
            products = products.filter(price__gte=min_price, stock__gte=1)
        if max_price is not None:
            products = products.filter(price__lte=max_price)
        if group:
            products = products.filter(group__in=group)
        if name:
            products = products.filter(name__icontains=name)
        if brand:
            products = products.filter(brand__in=brand)

    return render(
        request,
        "cosmetics_shop/main_page.html",
        {
            "title": "Главная страница",
            "group_product": group_product,
            "products": products,
            "count_cart_items": count_cart_items,
            "form": form,
        },
    )


@login_required
def logout_view(request):
    logout(request)
    return redirect("main_page")


@login_required
@transaction.atomic
def delete_account(request):
    user = request.user

    user.username = f"deleted_user_{uuid.uuid4().hex[:8]}"
    user.email = ""
    user.first_name = ""
    user.last_name = ""

    user.is_active = False
    user.save()

    logout(request)

    return redirect("main_page")


@login_required
def user_account(request):
    title = "Аккаунт"
    return render(
        request,
        "cosmetics_shop/user_account.html",
        {
            "title": title,
        },
    )


@login_required
def order_history(request):
    title = "История заказов"
    orders = Order.objects.filter(client=Client.objects.get(user=request.user))

    order_items = []

    for order in orders:
        dictt = {}
        dictt["order"] = order
        dictt["item"] = []
        items = OrderItem.objects.filter(order=order.id)
        if items.count() > 1:
            for item in items:
                dictt["order"] = order
                dictt["item"] += [item]
        else:
            dictt["item"] = items
        order_items.append(dictt)

    return render(
        request,
        "cosmetics_shop/order_history.html",
        {
            "title": title,
            "orders": orders,
            "order_items": order_items,
        },
    )


def category_page(request, category_id):
    group_product = GroupProduct.objects.filter(category=category_id)
    products = Product.objects.filter(group__in=group_product).order_by("-stock")
    return render(
        request,
        "cosmetics_shop/category_page.html",
        {
            "title": "Category",
            "group_product": group_product,
            "products": products,
        },
    )


def group_page(request, group_id):
    group_product = GroupProduct.objects.filter(id=group_id)
    products = Product.objects.filter(group__in=group_product).order_by("-stock")
    return render(
        request,
        "cosmetics_shop/category_page.html",
        {
            "title": "Category",
            "group_product": group_product,
            "products": products,
        },
    )


def product_page(request, product_code):
    product = Product.objects.get(code=product_code)
    return render(
        request,
        "cosmetics_shop/product_page.html",
        {
            "title": "Product",
            "product": product,
        },
    )


def brand_page(request):
    brands = Brand.objects.all()
    return render(
        request,
        "cosmetics_shop/brand.html",
        {
            "title": "Brands",
            "brands": brands,
        },
    )


def brand_products(request, brand_id):
    title = Brand.objects.get(id=brand_id)
    products = Product.objects.filter(brand=brand_id)
    return render(
        request,
        "cosmetics_shop/brand_products.html",
        {
            "title": title.name,
            "products": products,
        },
    )


def add_to_cart(request):
    product_code = request.POST.get("product_code")
    if not product_code:
        return redirect("main_page")

    if request.user.is_authenticated:
        add_product_to_cart(request, product_code=product_code)

    else:
        cart = get_or_create_cart_for_session(request)
        product = Product.objects.get(code=product_code)

        item, created = CartItem.objects.get_or_create(cart=cart, product=product)

        item.quantity += 1
        item.save()
    return redirect("main_page")


def cart(request):
    cart = get_or_create_cart(request)
    cart_items = CartItem.objects.select_related("product").filter(cart=cart)
    total_price = sum(item.product.price * item.quantity for item in cart_items)
    count_cart_items = sum(item.quantity for item in cart_items)

    return render(
        request,
        "cosmetics_shop/cart.html",
        {
            "title": "Корзина",
            "cart_items": cart_items,
            "total_price": total_price,
            "count_cart_items": count_cart_items,
        },
    )


def create_order(request, address_id):
    order = create_order_from_cart(request, address_id)
    if order:
        return redirect("order_success", order_id=order.id)
    return redirect("delivery")


def order_success(request, order_id):
    title = "Заказ"
    order = Order.objects.get(id=order_id)
    products = OrderItem.objects.filter(order=order)
    status = "Заказ успешно обработан"
    return render(
        request,
        "cosmetics_shop/order_success.html",
        {
            "title": title,
            "order": order,
            "products": products,
            "status": status,
        },
    )


@require_POST
def cart_add(request):
    product_code = request.POST.get("product_code")
    add_product_to_cart(request, product_code)
    return redirect("cart")


@require_POST
def cart_remove(request):
    product_code = request.POST.get("product_code")
    remove_product_from_cart(request, product_code)
    return redirect("cart")


@require_POST
def cart_delete(request):
    product_code = request.POST.get("product_code")
    delete_product_from_cart(request, product_code)
    return redirect("cart")


def delivery(request):
    title = "Оформление заказа"

    if request.method == "POST":
        form = ClientForm(request.POST)
        form_delivery = DeliveryAddressForm(request.POST)

        if form.is_valid() and form_delivery.is_valid():
            if request.user.is_authenticated:
                client, _ = Client.objects.get_or_create(user=request.user)
                client.full_name = form.cleaned_data["full_name"]
                client.email = form.cleaned_data["email"]
                client.phone = form.cleaned_data["phone"]
                client.is_active = True
                client.save()
            else:
                client = get_or_create_session_client(request, form)

            address = form_delivery.save(commit=False)
            address.client = client
            address.save()

            return redirect("order", address_id=address.id)

    else:
        try:
            client = get_client(request)
            last_address = (
                DeliveryAddress.objects.filter(client=client).order_by("-id").first()
            )
            form = ClientForm(instance=client)
            form_delivery = DeliveryAddressForm(instance=last_address)
        except Client.DoesNotExist:
            form = ClientForm()
            form_delivery = DeliveryAddressForm()

    return render(
        request,
        "cosmetics_shop/delivery.html",
        {
            "title": title,
            "form": form,
            "form_delivery": form_delivery,
        },
    )


def user_contact(request):
    if request.method == "POST":
        form = ClientForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect("user_contact")
    form = ClientForm(instance=request.user)
    return render(request, "cosmetics_shop/user_contact.html", {"form": form})
