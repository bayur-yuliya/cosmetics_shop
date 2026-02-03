import string
from typing import Optional, Dict, List

from django.contrib import messages
from django.contrib.auth import login, authenticate
from django.db.models import QuerySet, Sum, F
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from accounts.models import CustomUser
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
    Tag,
)
from .services.cart_services import (
    get_or_create_cart,
    delete_product_from_cart,
    get_or_create_session_client,
    delete_cart,
    is_product_in_cart,
)
from .services.categories_services import favorites_products
from .services.order_service import create_order_from_cart, get_client
from .utils.decorators import cart_required, order_session_required
from .utils.view_helpers import processing_product_page


def login_view(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        user: Optional[CustomUser] = authenticate(
            request, username=email, password=password
        )

        next_url = request.GET.get("next")
        if next_url and url_has_allowed_host_and_scheme(
            next_url, allowed_hosts={request.get_host()}
        ):
            next_url_path = next_url
        else:
            next_url_path = "main_page"

        if user is not None:
            login(request, user)
            messages.success(request, "Вы вошли")
        else:
            messages.error(request, "Неверный email или пароль")
        return redirect(next_url_path)

    return redirect("main_page")


def main_page(request: HttpRequest) -> HttpResponse:
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


def category_page(request: HttpRequest, category_id: int) -> HttpResponse:
    title: Category = Category.objects.get(pk=category_id)
    group_products: List[int] = list(
        GroupProduct.objects.filter(category=category_id).values_list("id", flat=True)
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


def group_page(request: HttpRequest, group_id: int) -> HttpResponse:
    title: GroupProduct = GroupProduct.objects.get(pk=group_id)

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


def product_page(request: HttpRequest, product_code: int) -> HttpResponse:
    product: Product = Product.objects.get(code=product_code)
    tags: QuerySet[Tag] = product.tags.all()
    is_it_in_cart = is_product_in_cart(request, product.id)
    return render(
        request,
        "cosmetics_shop/product_page.html",
        {
            "title": "Product",
            "product": product,
            "tags": tags,
            "is_it_in_cart": is_it_in_cart,
        },
    )


def brand_page(request: HttpRequest) -> HttpResponse:
    brands: QuerySet[Brand] = Brand.objects.all()
    grouped: Dict[str, List[Brand]] = {}

    for brand in brands:
        letter = brand.name[0].upper()
        grouped.setdefault(letter, []).append(brand)

    alphabet: List[str] = list(string.ascii_uppercase) + [
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


def brand_products(request: HttpRequest, brand_id: int) -> HttpResponse:
    title: Brand = Brand.objects.get(id=brand_id)

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


def cart(request: HttpRequest) -> HttpResponse:
    cart = get_or_create_cart(request)
    cart_items: QuerySet[CartItem] = CartItem.objects.select_related("product").filter(
        cart=cart
    )
    total_price = (
        cart_items.aggregate(total_price=Sum(F("product_price") * F("quantity")))[
            "total_price"
        ]
        or 0
    )

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
def create_order(request: HttpRequest, address_id: int) -> HttpResponse:
    order = create_order_from_cart(request, address_id)
    if order:
        request.session["order_id"] = order.id
        return redirect("order_success")
    return redirect("delivery")


@order_session_required
def order_success(request: HttpRequest) -> HttpResponse:
    order_id: Optional[int] = request.session.get("order_id")

    if order_id:
        order: Order = Order.objects.get(pk=order_id)
        products: QuerySet[OrderItem] = OrderItem.objects.filter(order=order)
        del request.session["order_id"]
    else:
        messages.error(request, "Возникла проблема с сохранением заказа")
        return redirect("main_page")

    return render(
        request,
        "cosmetics_shop/order_success.html",
        {
            "title": "Заказ",
            "order": order,
            "products": products,
            "status": "Заказ успешно обработан",
        },
    )


def clean_cart(request: HttpRequest) -> HttpResponse:
    delete_cart(request)
    return redirect("cart")


@require_POST
def cart_delete(request: HttpRequest) -> HttpResponse:
    product_id_row: Optional[str] = request.POST.get("product_id")
    if product_id_row is not None:
        product_id = int(product_id_row)
        delete_product_from_cart(request, product_id)
    else:
        messages.error(request, "Не удалось удалить товар")
    return redirect("cart")


@cart_required
def delivery(request: HttpRequest) -> HttpResponse:
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
            last_address: Optional[DeliveryAddress] = (
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
            "title": "Оформление заказа",
            "form": form,
            "form_delivery": form_delivery,
        },
    )


def payment_and_delivery(request: HttpRequest) -> HttpResponse:
    return render(request, "cosmetics_shop/payment_and_delivery_page.html")


def page_not_found(request: HttpRequest, exception: Exception) -> HttpResponse:
    return render(request, "cosmetics_shop/404_page_not_found.html", status=404)
