from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import OuterRef, Subquery, Count
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST

from cosmetics_shop.forms import ProductFilterForm
from cosmetics_shop.models import (
    Product,
    Order,
    OrderItem,
    OrderStatusLog,
    Brand,
    Category,
    Tag,
    GroupProduct,
    Favorite,
)
from stuff.forms import (
    ProductForm,
    OrderStatusForm,
    CategoryForm,
    GroupProductForm,
    BrandForm,
    TagForm,
    FilterStockForm,
)
from .services.dashboard_service import (
    number_of_orders_today,
    number_of_orders_per_month,
    summ_bill,
    average_bill,
)


@staff_member_required
def index(request):
    title = "Главная страница"

    orders_today = number_of_orders_today()
    orders_per_month = number_of_orders_per_month()
    summ = summ_bill()
    average = average_bill()
    max_favorite = (
        Favorite.objects.annotate(num_product=Count("product")).order_by("num_product")
    )[0:3]

    return render(
        request,
        "stuff/dashboard.html",
        {
            "title": title,
            "number_of_orders_today": orders_today,
            "number_of_orders_per_month": orders_per_month,
            "summ_bill": summ,
            "average_bill": average,
            "max_favorite": max_favorite,
        },
    )


@staff_member_required
def products(request):
    title = "Товары"
    products = Product.objects.all().order_by("-id")

    query_params = request.GET.copy()
    for key in list(query_params.keys()):
        if not query_params[key].strip():
            query_params.pop(key)
    if request.GET.urlencode() != query_params.urlencode():
        return redirect(f"{request.path}?{query_params.urlencode()}")

    form = ProductFilterForm(request.GET or None)
    form_stock = FilterStockForm(request.GET or None)

    if form.is_valid():
        name = form.cleaned_data["name"]
        group = form.cleaned_data["group"]
        tags = form.cleaned_data["tags"]
        min_price = form.cleaned_data["min_price"]
        max_price = form.cleaned_data["max_price"]
        brand = form.cleaned_data["brand"]

        if name:
            products = products.filter(name__icontains=name)
        if min_price is not None:
            products = products.filter(price__gte=min_price * 100, stock__gte=1)
        if max_price is not None:
            products = products.filter(price__lte=max_price * 100)
        if group:
            products = products.filter(group__in=group)
        if brand:
            products = products.filter(brand__in=brand)
        if tags:
            products = products.filter(tags__in=tags)

    if form_stock.is_valid():
        min_stock = form_stock.cleaned_data["min_stock"]
        max_stock = form_stock.cleaned_data["max_stock"]
        if min_stock:
            products = products.filter(stock__gte=min_stock)
        if max_stock:
            products = products.filter(stock__lte=max_stock)

    return render(
        request,
        "stuff/products.html",
        {
            "title": title,
            "products": products,
            "form": form,
            "form_stock": form_stock,
        },
    )


@staff_member_required
def product_card(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    tags = product.tags.all()
    return render(
        request,
        "stuff/product_card.html",
        {
            "product": product,
            "tags": tags,
        },
    )


@staff_member_required
def create_products(request):
    title = "Создание карточки товара"

    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.price = form.cleaned_data['price'] * 100
            product.save()
            return redirect("products")

    form = ProductForm()

    return render(
        request,
        "stuff/create_product.html",
        {
            "title": title,
            "form": form,
        },
    )


@staff_member_required
def edit_products(request, product_id):
    title = "Изменение товара"
    product = Product.objects.get(id=product_id)
    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            return redirect("product_card", product_id)
    form = ProductForm(instance=product)
    return render(
        request,
        "stuff/edit_product.html",
        {
            "title": title,
            "form": form,
        },
    )


@require_POST
@staff_member_required
def delete_product(request):
    product_id = request.POST.get("product_id")
    product = Product.objects.get(id=product_id)
    product.delete()
    return redirect("products")


@staff_member_required
def orders(request):
    title = "Список заказов"
    latest_status_subquery = OrderStatusLog.objects.filter(
        order=OuterRef("order")
    ).order_by("-changed_at")

    latest_statuses = OrderStatusLog.objects.filter(
        id__in=Subquery(latest_status_subquery.values("id")[:1])
    ).order_by("status")
    if request.method == "POST":
        form = OrderStatusForm(request.POST)
        if form.is_valid():
            latest_statuses = latest_statuses.filter(status=form.cleaned_data["status"])
            return render(
                request,
                "stuff/orders.html",
                {
                    "title": title,
                    "form": form,
                    "status": latest_statuses,
                },
            )
    else:
        form = OrderStatusForm()
    return render(
        request,
        "stuff/orders.html",
        {
            "title": title,
            "form": form,
            "status": latest_statuses,
        },
    )


@staff_member_required
def order_info(request, order_code):
    title = f"Заказ {order_code}"
    order = Order.objects.get(code=order_code)
    order_items = OrderItem.objects.filter(order=order)
    if request.method == "POST":
        form = OrderStatusForm(request.POST, instance=order)
        if form.is_valid():
            try:
                last = OrderStatusLog.objects.filter(order=order).first()
                if last.status != form.cleaned_data["status"]:
                    OrderStatusLog.objects.create(
                        order=order,
                        changed_by=request.user,
                        status=form.cleaned_data["status"],
                        comment=form.cleaned_data["comment"],
                    )
                    form.save()
                    messages.success(request, "Статус успешно изменен")
            except OrderStatusLog.DoesNotExists:
                OrderStatusLog.objects.create(
                    order=order,
                    changed_by=request.user,
                    status=form.cleaned_data["status"],
                    comment=form.cleaned_data["comment"],
                )
                form.save()
                messages.success(request, "Статус успешно изменен")
            return redirect("order_info", order_code=order.code)
    else:
        form = OrderStatusForm(instance=order)
        order_status_log = OrderStatusLog.objects.filter(order=order)

    return render(
        request,
        "stuff/order_info.html",
        {
            "title": title,
            "order": order,
            "order_items": order_items,
            "form": form,
            "order_status_log": order_status_log,
        },
    )


def brands_list(request):
    title = "Список брендов"
    list = Brand.objects.all()
    name = "brands"
    return render(
        request,
        "stuff/lists_page.html",
        {
            "title": title,
            "list": list,
            "name": name,
        },
    )


def categories_list(request):
    title = "Список категорий"
    list = Category.objects.all()
    return render(
        request,
        "stuff/lists_page.html",
        {
            "list": list,
            "title": title,
        },
    )


def tags_list(request):
    title = "Список тегов"
    list = Tag.objects.all()
    return render(
        request,
        "stuff/lists_page.html",
        {
            "list": list,
            "title": title,
        },
    )


def groups_list(request):
    title = " Список групп"
    list = GroupProduct.objects.all()
    return render(
        request,
        "stuff/lists_page.html",
        {
            "list": list,
            "title": title,
        },
    )


def create_categories(request):
    name = "Категория"
    if request.method == "POST":
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("categories_list")

    form = CategoryForm()
    return render(
        request,
        "stuff/create_page.html",
        {
            "name": name,
            "form": form,
        },
    )


def create_groups(request):
    name = "Группа"
    if request.method == "POST":
        form = GroupProductForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("groups_list")

    form = GroupProductForm()
    return render(
        request,
        "stuff/create_page.html",
        {
            "name": name,
            "form": form,
        },
    )


def create_brands(request):
    name = "Бренд"
    if request.method == "POST":
        form = BrandForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("brands_list")

    form = BrandForm()
    return render(
        request,
        "stuff/create_page.html",
        {
            "name": name,
            "form": form,
        },
    )


def create_tags(request):
    name = "Тег"
    if request.method == "POST":
        form = TagForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("tags_list")

    form = TagForm()
    return render(
        request,
        "stuff/create_page.html",
        {
            "name": name,
            "form": form,
        },
    )


@require_POST
def delete_tags(request):
    tag_id = request.POST.get("id")
    tag = get_object_or_404(Tag, id=tag_id)
    tag.delete()
    return redirect("tags_list")


@require_POST
def delete_categories(request):
    category_id = request.POST.get("id")
    category = get_object_or_404(Category, id=category_id)
    category.delete()
    return redirect("categories_list")


@require_POST
def delete_groups(request):
    group_id = request.POST.get("id")
    group = get_object_or_404(GroupProduct, id=group_id)
    group.delete()
    return redirect("groups_list")


@require_POST
def delete_brands(request):
    brand_id = request.POST.get("id")
    brand = get_object_or_404(Brand, id=brand_id)
    brand.delete()
    return redirect("brands_list")


def edit_categories(request, pk):
    category = get_object_or_404(Category, id=pk)

    if request.method == "POST":
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            return redirect("categories_list")

    form = CategoryForm(instance=category)
    return render(
        request,
        "stuff/edit_page.html",
        {
            "form": form,
        },
    )


def edit_groups(request, pk):
    group = get_object_or_404(GroupProduct, id=pk)

    if request.method == "POST":
        form = GroupProductForm(request.POST, instance=group)
        if form.is_valid():
            form.save()
            return redirect("groups_list")

    form = GroupProductForm(instance=group)
    return render(
        request,
        "stuff/edit_page.html",
        {
            "form": form,
        },
    )


def edit_brands(request, pk):
    brand = get_object_or_404(Brand, id=pk)

    if request.method == "POST":
        form = BrandForm(request.POST, instance=brand)
        if form.is_valid():
            form.save()
            return redirect("brands_list")

    form = BrandForm(instance=brand)
    return render(
        request,
        "stuff/edit_page.html",
        {
            "form": form,
        },
    )


def edit_tags(request, pk):
    tag = get_object_or_404(Tag, id=pk)

    if request.method == "POST":
        form = TagForm(request.POST, instance=tag)
        if form.is_valid():
            form.save()
            return redirect("tags_list")

    form = TagForm(instance=tag)
    return render(
        request,
        "stuff/edit_page.html",
        {
            "form": form,
        },
    )
