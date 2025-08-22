import uuid

from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.core.paginator import Paginator
from django.db import transaction
from django.shortcuts import render, redirect, get_object_or_404
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
    Category,
    OrderStatusLog,
    Favorite,
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

from .services.categories_services import context_categories, favorites_products


def register(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("login")
    form = UserCreationForm()
    return render(request, "registration/register.html", {"form": form})


def main_page(request):
    if request.user.is_authenticated:
        products = favorites_products(request)
    else:
        products = Product.objects.all()
    categories = context_categories()

    query_params = request.GET.copy()
    for key in list(query_params.keys()):
        if not query_params[key].strip():
            query_params.pop(key)
    if request.GET.urlencode() != query_params.urlencode():
        return redirect(f"{request.path}?{query_params.urlencode()}")

    form = ProductFilterForm(request.GET or None)

    if form.is_valid():
        name = form.cleaned_data["name"]
        group = form.cleaned_data["group"]
        tags = form.cleaned_data["tags"]
        min_price = form.cleaned_data["min_price"]
        max_price = form.cleaned_data["max_price"]
        brand = form.cleaned_data["brand"]

        if name:
            products = products.filter(name__icontains=name)
        if min_price is not None:
            products = products.filter(price__gte=min_price * 100, stock__gte=1)
        if max_price is not None:
            products = products.filter(price__lte=max_price * 100)
        if group:
            products = products.filter(group__in=group)
        if brand:
            products = products.filter(brand__in=brand)
        if tags:
            products = products.filter(tags__in=tags)

    paginator = Paginator(products, 20)
    page_number = request.GET.get("page")
    products = paginator.get_page(page_number)

    return render(
        request,
        "cosmetics_shop/main_page.html",
        {
            "title": "Главная страница",
            "context_categories": categories,
            "products": products,
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
    client, _ = Client.objects.get_or_create(user=request.user)
    orders = Order.objects.filter(client=client)
    order_items = []

    for order in orders:
        dictt = {}
        dictt["order"] = order
        dictt["item"] = []
        items = OrderItem.objects.filter(order=order.id)
        dictt["status"] = OrderStatusLog.objects.filter(order=order)[0]
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
            "order_items": order_items,
        },
    )


def category_page(request, category_id):
    title = Category.objects.get(id=category_id)
    categories = context_categories()
    group_product = GroupProduct.objects.filter(category=category_id)

    if request.user.is_authenticated:
        products = favorites_products(request).filter(group__in=group_product)

    paginator = Paginator(products, 20)
    page_number = request.GET.get("page")
    products = paginator.get_page(page_number)

    return render(
        request,
        "cosmetics_shop/category_page.html",
        {
            "title": title,
            "group_product": group_product,
            "products": products,
            "context_categories": categories,
        },
    )


def group_page(request, group_id):
    title = GroupProduct.objects.get(id=group_id)
    categories = context_categories()
    group_product = GroupProduct.objects.filter(id=group_id)

    if request.user.is_authenticated:
        products = favorites_products(request).filter(group__in=group_product)

    paginator = Paginator(products, 20)
    page_number = request.GET.get("page")
    products = paginator.get_page(page_number)

    return render(
        request,
        "cosmetics_shop/category_page.html",
        {
            "title": title,
            "group_product": group_product,
            "products": products,
            "context_categories": categories,
        },
    )


def product_page(request, product_code):
    product = Product.objects.get(code=product_code)
    tags = product.tags.all()
    return render(
        request,
        "cosmetics_shop/product_page.html",
        {
            "title": "Product",
            "product": product,
            "tags": tags,
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
    categories = context_categories()

    if request.user.is_authenticated:
        products = favorites_products(request).filter(brand=brand_id)

    paginator = Paginator(products, 20)
    page_number = request.GET.get("page")
    products = paginator.get_page(page_number)

    return render(
        request,
        "cosmetics_shop/category_page.html",
        {
            "title": title.name,
            "products": products,
            "context_categories": categories,
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
    next_url = request.GET.get("next", "/")
    return redirect(next_url)


def cart(request):
    cart = get_or_create_cart(request)
    cart_items = CartItem.objects.select_related("product").filter(cart=cart)
    total_price = sum(item.product.price * item.quantity for item in cart_items)

    return render(
        request,
        "cosmetics_shop/cart.html",
        {
            "title": "Корзина",
            "cart_items": cart_items,
            "total_price": total_price,
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
    next_url = request.GET.get("next", "/")
    return redirect(next_url)


@require_POST
def cart_remove(request):
    product_code = request.POST.get("product_code")
    remove_product_from_cart(request, product_code)
    next_url = request.GET.get("next", "/")
    return redirect(next_url)


@require_POST
def cart_delete(request):
    product_code = request.POST.get("product_code")
    delete_product_from_cart(request, product_code)
    next_url = request.GET.get("next", "/")
    return redirect(next_url)


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
    client = Client.objects.get(user=request.user)
    if request.method == "POST":
        form = ClientForm(request.POST, instance=client)
        if form.is_valid():
            form.save()
            return redirect("user_contact")
    form = ClientForm(instance=client)
    return render(
        request, "cosmetics_shop/user_contact.html", {"form": form, "client": client}
    )


@login_required
@require_POST
def add_to_favorites(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    Favorite.objects.get_or_create(user=request.user, product=product)
    next_url = request.GET.get("next", "/")
    return redirect(next_url)


@login_required
@require_POST
def remove_from_favorites(request, product_id):
    Favorite.objects.filter(user=request.user, product_id=product_id).delete()
    next_url = request.GET.get("next", "/")
    return redirect(next_url)


@login_required
def favorites(request):
    products = Favorite.objects.filter(user=request.user)

    paginator = Paginator(products, 20)
    page_number = request.GET.get("page")
    products = paginator.get_page(page_number)

    return render(
        request,
        "cosmetics_shop/favorites.html",
        {
            "title": "Избранное",
            "products": products,
            "is_favorite": True,
        },
    )
