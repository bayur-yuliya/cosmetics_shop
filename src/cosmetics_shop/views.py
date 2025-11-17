import string

from django.contrib import messages
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST

from .forms import (
    ClientForm,
    DeliveryAddressForm,
)
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
from .services.categories_services import favorites_products
from .services.order_service import create_order_from_cart, get_client
from .utils.decorators import cart_required, order_session_required
from .utils.view_helpers import processing_product_page


def login_view(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        user = authenticate(request, username=email, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, "Вы вошли")
            return redirect(request.META.get("HTTP_REFERER", "main_page"))
        else:
            messages.error(request, "Неверный email или пароль")
            return redirect(request.META.get("HTTP_REFERER", "main_page"))


def main_page(request):
    if request.user.is_authenticated:
        products = favorites_products(request)
    else:
        products = Product.objects.filter(is_active=True)

    return processing_product_page(
        request=request,
        products=products,
        title="Главная страница",
        template_name="cosmetics_shop/main_page.html",
    )


def category_page(request, category_id):
    title = Category.objects.get(id=category_id)
    group_products = GroupProduct.objects.filter(category=category_id).values_list(
        "id", flat=True
    )

    if request.user.is_authenticated:
        products = favorites_products(request).filter(group__in=group_products)
    else:
        products = Product.objects.filter(group__in=group_products)

    return processing_product_page(
        request=request,
        products=products,
        title=title,
        template_name="cosmetics_shop/category_page.html",
        hide_group_field=True,
    )


def group_page(request, group_id):
    title = GroupProduct.objects.get(id=group_id)

    if request.user.is_authenticated:
        products = favorites_products(request).filter(group=group_id)
    else:
        products = Product.objects.filter(group=group_id)

    return processing_product_page(
        request=request,
        title=title,
        products=products,
        template_name="cosmetics_shop/category_page.html",
        hide_group_field=True,
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
    grouped = {}
    for brand in brands:
        letter = brand.name[0].upper()
        grouped.setdefault(letter, []).append(brand)

    alphabet = list(string.ascii_uppercase) + [
        chr(code) for code in range(ord("А"), ord("Z") + 1)
    ]

    return render(
        request,
        "cosmetics_shop/brand.html",
        {
            "title": "Brands",
            "brands": brands,
            "grouped": grouped,
            "alphabet": alphabet,
        },
    )


def brand_products(request, brand_id):
    title = Brand.objects.get(id=brand_id)

    if request.user.is_authenticated:
        products = favorites_products(request).filter(brand=brand_id)
    else:
        products = Product.objects.filter(brand=brand_id)

    return processing_product_page(
        request=request,
        products=products,
        title=title,
        template_name="cosmetics_shop/category_page.html",
        hide_brands_field=True,
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


@cart_required
def create_order(request, address_id):
    order = create_order_from_cart(request, address_id)
    if order:
        request.session["order_id"] = order.id
        return redirect("order_success")
    return redirect("delivery")


@order_session_required
def order_success(request):
    title = "Заказ"
    order_id = request.session.get("order_id")
    status = "Заказ успешно обработан"
    if order_id:
        order = Order.objects.get(id=order_id)
        products = OrderItem.objects.filter(order=order)
        del request.session["order_id"]
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


@cart_required
def delivery(request):
    title = "Оформление заказа"

    if request.method == "POST":
        form = ClientForm(request.POST)
        form_delivery = DeliveryAddressForm(request.POST)

        if form.is_valid() and form_delivery.is_valid():
            if request.user.is_authenticated:
                client, _ = Client.objects.get_or_create(user=request.user)
                client.first_name = form.cleaned_data["first_name"]
                client.last_name = form.cleaned_data["last_name"]
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


@login_required
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


def payment_and_delivery(request):
    return render(request, "cosmetics_shop/payment_and_delivery_page.html")


def page_not_found(request, exception):
    return render(request, "cosmetics_shop/404_page_not_found.html", status=404)
