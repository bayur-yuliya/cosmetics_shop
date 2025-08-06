from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import OuterRef, Subquery
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST

from cosmetics_shop.models import (
    Product,
    Order,
    OrderItem,
    OrderStatusLog,
    Brand,
    Category,
    Tag,
    GroupProduct,
)
from stuff.forms import (
    ProductForm,
    OrderStatusForm,
    ProductFilterForm,
    CategoryForm,
    GroupProductForm,
    BrandForm,
    TagForm,
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

    return render(
        request,
        "stuff/dashboard.html",
        {
            "title": title,
            "number_of_orders_today": orders_today,
            "number_of_orders_per_month": orders_per_month,
            "summ_bill": summ,
            "average_bill": average,
        },
    )


@staff_member_required
def products(request):
    title = "Товары"
    products = Product.objects.all().order_by("-id")

    form = ProductFilterForm(request.GET or None)
    if form.is_valid():
        min_stock = form.cleaned_data["min_stock"]
        max_stock = form.cleaned_data["max_stock"]
        name = form.cleaned_data["name"]

        if min_stock is not None:
            products = products.filter(stock__gte=min_stock)
        if max_stock is not None:
            products = products.filter(stock__lte=max_stock)
        if name:
            products = products.filter(name__icontains=name)

    return render(
        request,
        "stuff/products.html",
        {
            "title": title,
            "products": products,
            "form": form,
        },
    )


@staff_member_required
def product_card(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    return render(
        request,
        "stuff/product_card.html",
        {
            "product": product,
        },
    )


@staff_member_required
def create_products(request):
    title = "Создание карточки товара"

    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
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
    )
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
    list = Brand.objects.all()
    name = "brands"
    return render(
        request,
        "stuff/lists_page.html",
        {
            "list": list,
            "name": name,
        },
    )


def categories_list(request):
    list = Category.objects.all()
    return render(
        request,
        "stuff/lists_page.html",
        {
            "list": list,
        },
    )


def tags_list(request):
    list = Tag.objects.all()
    return render(
        request,
        "stuff/lists_page.html",
        {
            "list": list,
        },
    )


def groups_list(request):
    list = GroupProduct.objects.all()
    return render(
        request,
        "stuff/lists_page.html",
        {
            "list": list,
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
