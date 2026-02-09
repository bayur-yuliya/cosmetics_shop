import string

from django.db.models import QuerySet
from django.http import HttpResponse, HttpRequest
from django.shortcuts import render

from cosmetics_shop.models import Brand, Tag, Product, GroupProduct, Category
from cosmetics_shop.services.cart_services import is_product_in_cart
from cosmetics_shop.services.product_service import get_ready_product_list
from cosmetics_shop.utils.view_helpers import processing_product_page
from utils.custom_types import AuthenticatedRequest


def main_page(request: HttpRequest) -> HttpResponse:
    products = get_ready_product_list(request)

    return processing_product_page(
        request=request,
        products=products,
        title="Главная страница",
        template_name="cosmetics_shop/main_page.html",
    )


def category_page(request: HttpRequest, category_id: int) -> HttpResponse:
    title: Category = Category.objects.get(pk=category_id)
    group_products: list[int] = list(
        GroupProduct.objects.filter(category=category_id).values_list("id", flat=True)
    )

    products = get_ready_product_list(request).filter(group__in=group_products)

    return processing_product_page(
        request=request,
        products=products,
        title=title,
        template_name="cosmetics_shop/category_page.html",
        hide_group_field=True,
    )


def group_page(
    request: HttpRequest | AuthenticatedRequest, group_id: int
) -> HttpResponse:
    title: GroupProduct = GroupProduct.objects.get(pk=group_id)

    products = get_ready_product_list(request).filter(group=group_id)

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
    is_it_in_cart = is_product_in_cart(request, product.pk)
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
    grouped: dict[str, list[Brand]] = {}

    for brand in brands:
        letter = brand.name[0].upper()
        grouped.setdefault(letter, []).append(brand)

    alphabet: list[str] = (
        list(string.ascii_uppercase)
        + [chr(code) for code in range(ord("А"), ord("Я") + 1)]
        + [chr(code) for code in range(ord("A"), ord("Z") + 1)]
    )

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
    products = get_ready_product_list(request).filter(brand=brand_id)

    return processing_product_page(
        request=request,
        products=products,
        title=title,
        template_name="cosmetics_shop/category_page.html",
        hide_brands_field=True,
    )
