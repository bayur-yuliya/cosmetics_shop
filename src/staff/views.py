import datetime

from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.models import Group
from django.core.paginator import Paginator
from django.db.models import OuterRef, Subquery, Count, Avg
from django.db.models.functions import TruncMonth
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.views.decorators.http import require_POST

from accounts.models import CustomUser
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
from staff.forms import (
    ProductForm,
    OrderStatusForm,
    CategoryForm,
    GroupProductForm,
    BrandForm,
    TagForm,
    FilterStockForm,
    ProductStuffFilterForm, GroupForm,
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
    today = datetime.date.today()
    orders_today = number_of_orders_today()
    orders_per_month = number_of_orders_per_month(today)
    summ = summ_bill(today)
    average = average_bill(today) / 100
    max_favorite = (
        Favorite.objects.annotate(num_product=Count("product")).order_by("num_product")
    )[0:3]
    current_year = timezone.now().year
    years = range(current_year - 5, current_year + 1)

    return render(
        request,
        "staff/dashboard.html",
        {
            "title": title,
            "number_of_orders_today": orders_today,
            "number_of_orders_per_month": orders_per_month,
            "summ_bill": summ,
            "average_bill": "{:10.2f}".format(average),
            "max_favorite": max_favorite,
            "years": years,
            "current_year": current_year,
        },
    )


def sales_comparison_chart_for_the_year(request):
    year = request.GET.get("year")
    now = timezone.now()

    try:
        year = int(year)
    except (TypeError, ValueError):
        year = now.year

    orders_by_month = (
        Order.objects.filter(created_at__year=year)
        .annotate(month=TruncMonth("created_at"))
        .values("month")
        .annotate(
            count=Count("id"),
            avg_price=Avg("total_price"),
        )
    )
    sales_counts = [0] * 12
    average_bill_counts = [0] * 12
    for item in orders_by_month:
        month = item["month"].month - 1
        sales_counts[month] = item["count"]
        price = item["avg_price"] / 100
        average_bill_counts[month] = round(price or 0, 2)

    return JsonResponse(
        {
            "labels": [
                "Янв",
                "Фев",
                "Мар",
                "Апр",
                "Май",
                "Июн",
                "Июл",
                "Авг",
                "Сен",
                "Окт",
                "Ноя",
                "Дек",
            ],
            "year": year,
            "sales": sales_counts,
            "average_bill": average_bill_counts,
        }
    )


def is_superuser(user):
    return user.is_superuser


@user_passes_test(is_superuser)
def staff_group_list(request):
    groups = Group.objects.all()

    return render(request, "staff/staff_groups_list.html", {"groups": groups})


@user_passes_test(is_superuser)
def staff_group_edit(request, pk=None):
    group = get_object_or_404(Group, pk=pk) if pk else None
    form = GroupForm(request.POST or None, instance=group)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("groups:list")
    return render(request, "staff/edit_staff_groups.html", {"form": form})


@user_passes_test(is_superuser)
def staff_list(request):
    staffs = CustomUser.objects.all()
    return render(request, "staff/staff_list.html", {"staffs": staffs})


@staff_member_required
def products(request):
    title = "Товары"
    products = Product.objects.all().order_by("-id").filter(is_active=True)

    query_params = request.GET.copy()
    for key in list(query_params.keys()):
        if not query_params[key].strip():
            query_params.pop(key)
    if request.GET.urlencode() != query_params.urlencode():
        return redirect(f"{request.path}?{query_params.urlencode()}")

    form = ProductStuffFilterForm(request.GET or None)
    form_stock = FilterStockForm(request.GET or None)

    if form.is_valid():
        name = form.cleaned_data["name"]
        code = form.cleaned_data["code"]
        min_price = form.cleaned_data["min_price"]
        max_price = form.cleaned_data["max_price"]

        if name:
            products = products.filter(name__icontains=name)
        if min_price is not None:
            products = products.filter(price__gte=min_price * 100, stock__gte=1)
        if max_price is not None:
            products = products.filter(price__lte=max_price * 100)
        if code:
            products = products.filter(code__icontains=code)

    if form_stock.is_valid():
        min_stock = form_stock.cleaned_data["min_stock"]
        max_stock = form_stock.cleaned_data["max_stock"]
        if min_stock:
            products = products.filter(stock__gte=min_stock)
        if max_stock:
            products = products.filter(stock__lte=max_stock)

    paginator = Paginator(products, 20)
    page_number = request.GET.get("page")
    products = paginator.get_page(page_number)

    return render(
        request,
        "staff/products.html",
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
    title = product.name
    tags = product.tags.all()
    return render(
        request,
        "staff/product_card.html",
        {
            "title": title,
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
            saved_product = form.save(commit=False)
            saved_product.price = form.cleaned_data["price"] * 100
            saved_product.save()
            form.save_m2m()
            return redirect("products")

    form = ProductForm()

    return render(
        request,
        "staff/create_product.html",
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
            saved_product = form.save(commit=False)
            saved_product.price = form.cleaned_data["price"] * 100
            saved_product.save()
            form.save_m2m()
            return redirect("product_card", product_id)
    form = ProductForm(instance=product)
    return render(
        request,
        "staff/edit_product.html",
        {
            "title": title,
            "form": form,
            "product": product,
        },
    )


@require_POST
@staff_member_required
def delete_product(request):
    product_id = request.POST.get("product_id")
    product = Product.objects.get(id=product_id)
    product.is_active = False
    product.save()
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
            status = form.cleaned_data.get("status")
            date_from = form.cleaned_data.get("date_from")
            date_to = form.cleaned_data.get("date_to")
            if status:
                latest_statuses = latest_statuses.filter(status=status)

            if date_from:
                latest_statuses = latest_statuses.filter(
                    order__created_at__gte=date_from
                )
            if date_to:
                latest_statuses = latest_statuses.filter(order__created_at__lte=date_to)

            return render(
                request,
                "staff/orders.html",
                {
                    "title": title,
                    "form": form,
                    "status": latest_statuses,
                },
            )
    else:
        form = OrderStatusForm()

    paginator = Paginator(latest_statuses, 20)
    page_number = request.GET.get("page")
    latest_statuses = paginator.get_page(page_number)

    return render(
        request,
        "staff/orders.html",
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
        "staff/order_info.html",
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
        "staff/lists_page.html",
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
        "staff/lists_page.html",
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
        "staff/lists_page.html",
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
        "staff/lists_page.html",
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
        "staff/create_page.html",
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
        "staff/create_page.html",
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
        "staff/create_page.html",
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
        "staff/create_page.html",
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
        "staff/edit_page.html",
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
        "staff/edit_page.html",
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
        "staff/edit_page.html",
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
        "staff/edit_page.html",
        {
            "form": form,
        },
    )
