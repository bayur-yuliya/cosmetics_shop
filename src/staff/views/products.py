import logging

from django.contrib import messages
from django.contrib.auth.decorators import permission_required
from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from cosmetics_shop.models import (
    Product,
    Tag,
)
from staff.forms import ProductFilterForm, ProductForm
from utils.helper_function import get_paginator_page

logger = logging.getLogger(__name__)


@permission_required("cosmetics_shop.view_product", raise_exception=True)
def products(request: HttpRequest) -> HttpResponse:
    logger.debug(f"Products list opened: user_id={request.user.id}")

    products_list = (
        Product.objects.all().order_by("-id").filter(is_active=True).for_catalog()
    )

    form = ProductFilterForm(request.GET)

    if form.is_valid():
        logger.debug(f"Product filters applied: {form.cleaned_data}")
        products_list = form.apply_filters(products_list)

    page = get_paginator_page(request, products_list)

    logger.info(
        f"Products page loaded: user_id={request.user.id}, count={page.paginator.count}"
    )

    return render(
        request,
        "staff/products.html",
        {
            "title": "Товары",
            "products": page,
            "form": form,
        },
    )


@permission_required("cosmetics_shop.view_product", raise_exception=True)
def archive_products(request: HttpRequest) -> HttpResponse:
    logger.debug(f"Products list opened: user_id={request.user.id}")

    products_list = (
        Product.objects.all().order_by("-id").filter(is_active=False).for_catalog()
    )

    page = get_paginator_page(request, products_list)

    logger.info(
        f"Products page loaded: user_id={request.user.id}, count={page.paginator.count}"
    )

    return render(
        request,
        "staff/archive_page.html",
        {
            "title": "Товары",
            "products": page,
        },
    )


@permission_required("cosmetics_shop.view_product", raise_exception=True)
def product_card(request: HttpRequest, product_code: int) -> HttpResponse:
    logger.debug(
        f"Product card opened: product_code={product_code}, user_id={request.user.id}"
    )

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
        logger.info(f"Product creation attempt: user_id={request.user.id}")

        form = ProductForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            product = form.save()
            logger.info(
                f"Product created: product_id={product.id}, user_id={request.user.id}"
            )
            return redirect("products")
        else:
            logger.warning(f"Invalid product form: errors={form.errors}")
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

    logger.debug(
        f"Edit product page: product_id={product.id}, user_id={request.user.id}"
    )

    if request.method == "POST":
        logger.info(
            f"Product update attempt: product_id={product.id},"
            f" user_id={request.user.id}"
        )

        form = ProductForm(
            request.POST, request.FILES, instance=product, user=request.user
        )

        if form.is_valid():
            form.save()
            logger.info(
                f"Product updated: product_id={product.id}, user_id={request.user.id}"
            )
            return redirect("product_card", product_code=product_code)
        else:
            logger.warning(f"Invalid product update form: errors={form.errors}")

    else:
        form = ProductForm(instance=product, user=request.user)
    print(f"Form initial data: {dict(form.initial)}")
    print(f"Form fields: {list(form.fields.keys())}")
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
        logger.info(
            f"Product delete attempt: product_id={product_id},"
            f" user_id={request.user.id}"
        )
        product: Product = get_object_or_404(Product, id=product_id)
        product.soft_delete()

        logger.info(f"Product soft deleted: product_id={product_id}")
    else:
        logger.warning("Delete product called without product_id")

        messages.error(request, "Не удалось удалить товар")
    return redirect("products")


@require_POST
@permission_required("staff.hard_delete_and_recovery_products", raise_exception=True)
def hard_delete_products(request: HttpRequest, product_id: int) -> HttpResponse:
    if not product_id:
        logger.warning("Hard delete called without product_id")
        messages.error(request, "Не удалось удалить товар")
        return redirect("products")

    product = get_object_or_404(Product, id=product_id)

    logger.info(
        f"Hard delete attempt: product_id={product_id}, user_id={request.user.id}"
    )

    if hasattr(product, "orders") and product.orders.exists():
        logger.warning(f"Hard delete denied (has orders): product_id={product_id}")
        messages.error(request, "Нельзя удалить товар с заказами")
        return redirect("products")

    product.delete()

    logger.info(f"Product hard deleted: product_id={product_id}")
    messages.success(request, "Товар удалён навсегда")

    return redirect("products")


@require_POST
@permission_required("staff.hard_delete_and_recovery_products", raise_exception=True)
def recovery_products(request: HttpRequest, product_id: int) -> HttpResponse:
    if not product_id:
        logger.warning("Recovery called without product_id")
        messages.error(request, "Не удалось восстановить товар")
        return redirect("products")

    product = get_object_or_404(Product, id=product_id)

    logger.info(
        f"Product recovery attempt: product_id={product_id}, user_id={request.user.id}"
    )

    product.is_active = True
    product.save()

    logger.info(f"Product restored: product_id={product_id}")
    messages.success(request, "Товар восстановлен")

    return redirect("products")
