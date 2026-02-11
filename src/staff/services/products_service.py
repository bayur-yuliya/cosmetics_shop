from django.db.models import QuerySet

from cosmetics_shop.models import Product


def filter_staff_form(products_list: QuerySet[Product], form) -> QuerySet[Product]:
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
    return products_list


def filter_staff_stock_form(
    products_list: QuerySet[Product], form
) -> QuerySet[Product]:
    if form.is_valid():
        min_stock = form.cleaned_data["min_stock"]
        max_stock = form.cleaned_data["max_stock"]
        if min_stock:
            products_list = products_list.filter(stock__gte=min_stock)
        if max_stock:
            products_list = products_list.filter(stock__lte=max_stock)
    return products_list
