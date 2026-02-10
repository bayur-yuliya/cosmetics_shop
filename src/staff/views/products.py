from django.contrib import messages
from django.contrib.auth.decorators import permission_required
from django.core.paginator import Paginator
from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404

from django.views.decorators.http import require_POST

from cosmetics_shop.models import (
    Product,
    Tag,
)
from staff.forms import (
    ProductForm,
    FilterStockForm,
    ProductStuffFilterForm,
)


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

    if form.is_valid():
        name = form.cleaned_data["name"]
        code = form.cleaned_data["code"]
        brand = form.cleaned_data["brand"]
        min_price = form.cleaned_data["min_price"]
        max_price = form.cleaned_data["max_price"]

        if name:
            products_list = products_list.filter(name__icontains=name)
        if brand:
            products_list = products_list.filter(brand__name__icontains=brand)
        if min_price is not None:
            products_list = products_list.filter(
                price__gte=min_price * 100, stock__gte=1
            )
        if max_price is not None:
            products_list = products_list.filter(price__lte=max_price * 100)
        if code:
            products_list = products_list.filter(code__icontains=code)

    if form_stock.is_valid():
        min_stock = form_stock.cleaned_data["min_stock"]
        max_stock = form_stock.cleaned_data["max_stock"]
        if min_stock:
            products_list = products_list.filter(stock__gte=min_stock)
        if max_stock:
            products_list = products_list.filter(stock__lte=max_stock)

    paginator = Paginator(products_list, 20)
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
