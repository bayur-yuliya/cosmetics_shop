from django.core.paginator import Paginator
from django.shortcuts import redirect, render

from cosmetics_shop.forms import ProductFilterForm
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
    query_params = request.GET.copy()
    for key in list(query_params.keys()):
        if not query_params[key].strip():
            query_params.pop(key)
    if request.GET.urlencode() != query_params.urlencode():
        return redirect(f"{request.path}?{query_params.urlencode()}")

    if request.GET.get("sort") == "None" or not request.GET.get("sort"):
        clean_params = request.GET.copy()
        clean_params.pop("sort", None)
        clean_params.pop("direction", None)
        clean_url = "?" + clean_params.urlencode() if clean_params else "."
        if request.GET.get("sort"):
            return redirect(f"{request.path}{clean_url}")
    categories = context_categories()
    product_filter = ProductFilter(request, products)
    form = ProductFilterForm(request.GET or None)

    if form.is_valid():
        products = product_filter.apply_filters(form)

    products = product_filter.apply_sorting()

    paginator = Paginator(products, 20)
    page_number = request.GET.get("page")
    products = paginator.get_page(page_number)

    context = {
        "title": title,
        "context_categories": categories,
        "products": products,
        "form": form,
        "product_filter": product_filter,
        "current_sort": product_filter.current_sort,
        "current_direction": product_filter.current_direction,
        "hide_brands_field": hide_brands_field,
        "hide_group_field": hide_group_field,
    }
    if extra_context:
        context.update(extra_context)

    return render(request, template_name, context)
