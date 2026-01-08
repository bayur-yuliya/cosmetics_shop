from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.template.loader import render_to_string

from cosmetics_shop.forms import ProductFilterForm
from cosmetics_shop.models import CartItem
from cosmetics_shop.services.cart_services import get_or_create_cart, get_id_products_in_cart
from cosmetics_shop.services.categories_services import context_categories
from cosmetics_shop.utils.product_filter import ProductFilter


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

    query_params = request.GET.copy()
    for key, value in list(query_params.items()):
        if value in ("", "None", None):
            query_params.pop(key)

    clean_url = (
        f"{request.path}?{query_params.urlencode()}"
        if query_params else request.path
    )

    product_filter = ProductFilter(request, products)
    form = ProductFilterForm(request.GET or None)

    if form.is_valid():
        product_filter.apply_filters(form)

    cart_products = get_id_products_in_cart(request)
    products = product_filter.apply_sorting()

    paginator = Paginator(products, 20)
    page_number = request.GET.get("page")
    products = paginator.get_page(page_number)
    categories = context_categories()
    context = {
        "title": title,
        "products": products,
        "form": form,
        "product_filter": product_filter,
        "context_categories": categories,
        "current_sort": product_filter.current_sort,
        "current_direction": product_filter.current_direction,
        "hide_brands_field": hide_brands_field,
        "hide_group_field": hide_group_field,
        "cart_products": cart_products,
    }

    if clean_url != request.get_full_path():
        if not is_ajax:
            return redirect(clean_url)

    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        html = render_to_string(
            "cosmetics_shop/includes/product_list.html",
            context,
            request=request,
        )
        return JsonResponse({
            "html": html,
            "url": clean_url,
        })

    if extra_context:
        context.update(extra_context)

    return render(request, template_name, context)
