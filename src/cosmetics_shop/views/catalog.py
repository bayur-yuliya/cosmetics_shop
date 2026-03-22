from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, render

from cosmetics_shop.models import Brand, Category, GroupProduct, Product, Tag
from cosmetics_shop.services.cart_services import is_product_in_cart
from cosmetics_shop.utils.cart_utils import get_cart
from cosmetics_shop.utils.context_utils import get_grouped_for_alphabet_brands
from cosmetics_shop.utils.product_utils import get_ready_product_list
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


def category_page(request: HttpRequest, category_slug: str) -> HttpResponse:
    title: Category = get_object_or_404(Category, slug=category_slug)
    products = get_ready_product_list(request)

    return processing_product_page(
        request=request,
        products=products,
        title=title,
        template_name="cosmetics_shop/category_page.html",
        hide_group_field=True,
    )


def group_page(
    request: HttpRequest | AuthenticatedRequest, group_slug: str
) -> HttpResponse:
    title: GroupProduct = get_object_or_404(GroupProduct, slug=group_slug)
    products = get_ready_product_list(request).filter(group=title)

    return processing_product_page(
        request=request,
        title=title,
        products=products,
        template_name="cosmetics_shop/category_page.html",
        hide_group_field=True,
    )


def product_page(request: HttpRequest, product_code: int) -> HttpResponse:
    product: Product = get_object_or_404(Product, code=product_code)
    tags: QuerySet[Tag] = product.tags.all()
    cart = get_cart(request)
    is_it_in_cart = is_product_in_cart(cart, product.pk)
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
    grouped = get_grouped_for_alphabet_brands(brands)
    alphabet: list[str] = list(grouped.keys())

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


def brand_products(request: HttpRequest, brand_slug: str) -> HttpResponse:
    title: Brand = get_object_or_404(Brand, slug=brand_slug)
    products = get_ready_product_list(request).filter(brand=title)

    return processing_product_page(
        request=request,
        products=products,
        title=title,
        template_name="cosmetics_shop/category_page.html",
        hide_brands_field=True,
    )
