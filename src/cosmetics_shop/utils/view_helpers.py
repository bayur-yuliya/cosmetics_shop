from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.template.loader import render_to_string

from cosmetics_shop.forms import ProductFilterForm
from cosmetics_shop.models import CartItem
from cosmetics_shop.services.cart_services import get_or_create_cart
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
    query_params = request.GET.copy()
    for key in list(query_params.keys()):
        if not query_params[key].strip():
            query_params.pop(key)

    product_filter = ProductFilter(request, products)
    form = ProductFilterForm(request.GET or None)

    if form.is_valid():
        products = product_filter.apply_filters(form)

    cart = get_or_create_cart(request)
    cart_products = set()
    if cart:
        cart_products = set(
            CartItem.objects.filter(cart=cart)
            .values_list("product_id", flat=True)
        )
    products = product_filter.apply_sorting()

    paginator = Paginator(products, 20)
    page_number = request.GET.get("page")
    products = paginator.get_page(page_number)

    context = {
        "title": title,
        "products": products,
        "form": form,
        "product_filter": product_filter,
        "current_sort": product_filter.current_sort,
        "current_direction": product_filter.current_direction,
        "hide_brands_field": hide_brands_field,
        "hide_group_field": hide_group_field,
        "cart_products": cart_products,
    }

    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        html = render_to_string(
            "cosmetics_shop/includes/product_list.html",
            context,
            request=request,
        )
        return JsonResponse({"html": html})

    if extra_context:
        context.update(extra_context)

    return render(request, template_name, context)
