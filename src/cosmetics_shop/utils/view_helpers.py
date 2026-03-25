import logging

from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.template.loader import render_to_string

from cosmetics_shop.forms import ProductFilterForm
from cosmetics_shop.services.cart_services import (
    get_id_products_in_cart,
)
from cosmetics_shop.utils.cart_utils import get_cart
from cosmetics_shop.utils.context_utils import context_categories
from cosmetics_shop.utils.product_filters import ProductFilter
from utils.helper_function import get_paginator_page

logger = logging.getLogger(__name__)


def clean_query_params(request):
    query_params = request.GET.copy()

    removed_keys = []

    for key, value in list(query_params.items()):
        if value in ("", "None", None):
            query_params.pop(key)
            removed_keys.append(key)

    if removed_keys:
        logger.debug("Removed empty query params", extra={"keys": removed_keys})

    clean_url = (
        f"{request.path}?{query_params.urlencode()}" if query_params else request.path
    )
    return query_params, clean_url


def build_context(request, products, title, extra_context=None, **kwargs):
    logger.debug("Building product context", extra={"title": title})

    product_filter = ProductFilter(request, products)
    form = ProductFilterForm(request.GET or None)

    if form.is_valid():
        product_filter.apply_filters(form)
        logger.debug("Filters applied", extra={"filters": form.cleaned_data})
    else:
        logger.debug("Invalid filter form")

    cart = get_cart(request)
    cart_products = get_id_products_in_cart(cart)
    products = product_filter.apply_sorting()

    page = get_paginator_page(request, products)
    categories = context_categories()

    logger.debug(
        "Pagination applied",
        extra={"page": request.GET.get("page"), "count": page.paginator.count},
    )

    context = {
        "title": title,
        "products": page,
        "form": form,
        "product_filter": product_filter,
        "context_categories": categories,
        "current_sort": product_filter.current_sort,
        "current_direction": product_filter.current_direction,
        "hide_brands_field": kwargs.get("hide_brands_field", False),
        "hide_group_field": kwargs.get("hide_group_field", False),
        "cart_products": cart_products,
    }

    if extra_context:
        context.update(extra_context)

    return context


def handle_ajax(request, context, clean_url):
    logger.debug("Handling AJAX request")

    html = render_to_string(
        "cosmetics_shop/includes/product_list.html",
        context,
        request=request,
    )
    html_sorting = render_to_string(
        "cosmetics_shop/includes/sorting_panel.html",
        context,
        request=request,
    )
    return JsonResponse(
        {
            "html": html,
            "url": clean_url,
            "sorting_html": html_sorting,
        }
    )


def processing_product_page(
    request,
    products,
    template_name,
    title,
    extra_context=None,
    hide_group_field=False,
    hide_brands_field=False,
):
    is_ajax = request.headers.get("X-Requested-With") == "XMLHttpRequest"

    logger.debug(
        "Processing product page",
        extra={"is_ajax": is_ajax, "path": request.path},
    )

    query_params, clean_url = clean_query_params(request)

    context = build_context(
        request,
        products,
        title,
        extra_context,
        hide_group_field=hide_group_field,
        hide_brands_field=hide_brands_field,
    )

    if clean_url != request.get_full_path() and not is_ajax:
        logger.debug("Redirecting to clean URL", extra={"url": clean_url})
        return redirect(clean_url)

    if is_ajax:
        return handle_ajax(request, context, clean_url)

    return render(request, template_name, context)
