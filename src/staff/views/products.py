from django.contrib import messages
from django.contrib.auth.decorators import permission_required
from django.core.paginator import Paginator
from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404

from django.views.decorators.http import require_POST

from config.settings import PRODUCTS_PER_PAGE
from cosmetics_shop.models import (
    Product,
    Tag,
)
from staff.forms import (
    ProductForm,
    FilterStockForm,
    ProductStuffFilterForm,
)
from staff.services.products_service import filter_staff_form, filter_staff_stock_form


@permission_required("cosmetics_shop.view_product", raise_exception=True)
def products(request: HttpRequest) -> HttpResponse:
    products_list = (
        Product.objects.all()
        .order_by("-id")
        .filter(is_active=True)
        .select_related("brand")
    )

    form = ProductStuffFilterForm(request.GET or None)
    form_stock = FilterStockForm(request.GET or None)

    filtered_product: QuerySet[Product] = filter_staff_form(products_list, form)
    stock_filtered_product: QuerySet[Product] = filter_staff_stock_form(
        filtered_product, form_stock
    )

    paginator = Paginator(stock_filtered_product, PRODUCTS_PER_PAGE)
    page_number = request.GET.get("page")
    page = paginator.get_page(page_number)

    return render(
        request,
        "staff/products.html",
        {
            "title": "Товары",
            "products": page,
            "form": form,
            "form_stock": form_stock,
        },
    )


@permission_required("cosmetics_shop.view_product", raise_exception=True)
def product_card(request: HttpRequest, product_code: int) -> HttpResponse:
    product = get_object_or_404(Product, code=product_code)
    title = product.name
    tags: QuerySet[Tag] = product.tags.all()
    return render(
        request,
        "staff/product_card.html",
        {
            "title": title,
            "product": product,
            "tags": tags,
        },
    )


@permission_required("cosmetics_shop.add_product", raise_exception=True)
def create_products(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect("products")
    form = ProductForm()

    return render(
        request,
        "staff/product_management.html",
        {
            "title": "Создание карточки товара",
            "form": form,
        },
    )


@permission_required("cosmetics_shop.change_product", raise_exception=True)
def edit_products(request: HttpRequest, product_code: int) -> HttpResponse:
    product = get_object_or_404(Product, code=product_code)
    if request.method == "POST":
        form = ProductForm(
            request.POST, request.FILES, instance=product, user=request.user
        )
        if form.is_valid():
            form.save()
            return redirect("product_card", product_code=product_code)
    form = ProductForm(instance=product, user=request.user)
    return render(
        request,
        "staff/product_management.html",
        {
            "title": "Изменение товара",
            "form": form,
            "product": product,
        },
    )


@require_POST
@permission_required("cosmetics_shop.delete_product", raise_exception=True)
def delete_product(request: HttpRequest, product_id: int) -> HttpResponse:
    if product_id:
        product: Product = get_object_or_404(Product, id=product_id)
        product.is_active = False
        product.save()
    else:
        messages.error(request, "Не удалось удалить товар")
    return redirect("products")
