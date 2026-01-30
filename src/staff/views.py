import datetime

from django.contrib import messages
from django.contrib.auth.decorators import permission_required
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
    ProductStuffFilterForm,
    GroupForm,
)
from .services.dashboard_service import (
    number_of_completed_orders_today,
    number_of_orders_per_month,
    summ_bill,
    average_bill,
)
from .services.list_service import staff_list_view
from .services.permission_service import get_individually_assigned_permits


@permission_required("staff.dashboard_view", raise_exception=False)
def index(request):
    title = "Главная страница"
    today = datetime.date.today()
    completed_orders_today = number_of_completed_orders_today()
    orders_per_month = number_of_orders_per_month(today)
    summ = summ_bill(today)
    average = "{:10.2f}".format(average_bill(today) / 100)
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
            "number_of_completed_orders_today": completed_orders_today,
            "number_of_orders_per_month": orders_per_month,
            "summ_bill": summ,
            "average_bill": average,
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


@permission_required("staff.manage_permission", raise_exception=True)
def staff_group_list(request):
    groups = Group.objects.annotate(user_count=Count("user")).prefetch_related(
        "permissions"
    )

    return render(
        request,
        "staff/permissions/groups_list.html",
        {"title": "Список групп разрешений", "groups": groups},
    )


@permission_required("staff.manage_permission", raise_exception=True)
def staff_group_edit(request, pk=None):
    group = get_object_or_404(Group, pk=pk) if pk else None
    form = GroupForm(request.POST or None, instance=group)
    if request.method == "POST" and form.is_valid():
        form.save()

        return redirect("staff_groups_list")
    return render(
        request,
        "staff/permissions/edit_groups.html",
        {
            "title": "Страница управления разрешениями",
            "group": group,
            "form": form,
        },
    )


@permission_required("staff.manage_permission", raise_exception=True)
def staff_list(request):
    staffs = CustomUser.objects.filter(is_staff=True).prefetch_related(
        "groups", "user_permissions"
    )
    return render(
        request,
        "staff/permissions/staff_list.html",
        {"title": "Страница сотрудников", "staffs": staffs},
    )


@permission_required("staff.manage_permission", raise_exception=True)
def edit_staff_permissions(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)

    if request.method == "POST":
        selected_groups = request.POST.getlist("groups")

        user.groups.clear()
        for group_id in selected_groups:
            group = Group.objects.get(id=group_id)
            user.groups.add(group)

        selected_perm_ids = request.POST.getlist("permissions")

        user.user_permissions.set(selected_perm_ids)

        return redirect("staff_list")

    all_groups = Group.objects.all()
    user_groups = user.groups.all()

    permissions = get_individually_assigned_permits()

    permissions_by_app = {}
    for perm in permissions:
        app_label = perm.content_type.app_label
        if app_label not in permissions_by_app:
            permissions_by_app[app_label] = []
        permissions_by_app[app_label].append(perm)

    return render(
        request,
        "staff/permissions/edit_staff_permissions.html",
        {
            "user": user,
            "title": "Изменение разрешений",
            "all_groups": all_groups,
            "user_groups": user_groups,
            "permissions_by_app": permissions_by_app,
            "user_permissions": user.user_permissions.all(),
        },
    )


@permission_required("cosmetics_shop.view_product", raise_exception=True)
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


@permission_required("cosmetics_shop.view_product", raise_exception=True)
def product_card(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
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


@permission_required("cosmetics_shop.add_product", raise_exception=True)
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
        "staff/create_product.html",
        {
            "title": title,
            "form": form,
        },
    )


@permission_required("cosmetics_shop.change_product", raise_exception=True)
def edit_products(request, product_id):
    title = "Изменение товара"
    product = get_object_or_404(Product, pk=product_id)
    if request.method == "POST":
        form = ProductForm(
            request.POST, request.FILES, instance=product, user=request.user
        )
        if form.is_valid():
            form.save()
            return redirect("product_card", product_id=product_id)
    form = ProductForm(instance=product, user=request.user)
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
@permission_required("cosmetics_shop.delete_product", raise_exception=True)
def delete_product(request):
    product_id = request.POST.get("product_id")
    product = Product.objects.get(id=product_id)
    product.is_active = False
    product.save()
    return redirect("products")


@permission_required("cosmetics_shop.view_order", raise_exception=True)
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


@permission_required("cosmetics_shop.view_order", raise_exception=True)
def order_info(request, order_code):
    title = f"Заказ {order_code}"
    order = Order.objects.get(code=order_code)
    order_items = OrderItem.objects.filter(order=order)
    if request.method == "POST":
        form = OrderStatusForm(request.POST, instance=order, user=request.user)
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
        form = OrderStatusForm(instance=order, user=request.user)
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


@permission_required("cosmetics_shop.view_brand", raise_exception=True)
def brands_list(request):
    title = "Список брендов"
    list = Brand.objects.all()
    return staff_list_view(
        request,
        "staff/lists_page.html",
        {
            "title": title,
            "list": list,
        },
    )


@permission_required("cosmetics_shop.view_category", raise_exception=True)
def categories_list(request):
    title = "Список категорий"
    list = Category.objects.all()
    return staff_list_view(
        request,
        "staff/lists_page.html",
        {
            "list": list,
            "title": title,
        },
    )


@permission_required("cosmetics_shop.view_tag", raise_exception=True)
def tags_list(request):
    title = "Список тегов"
    list = Tag.objects.all()
    return staff_list_view(
        request,
        "staff/lists_page.html",
        {
            "list": list,
            "title": title,
        },
    )


@permission_required("cosmetics_shop.view_groupproduct", raise_exception=True)
def groups_list(request):
    title = " Список групп"
    list = GroupProduct.objects.all()
    return staff_list_view(
        request,
        "staff/lists_page.html",
        {
            "list": list,
            "title": title,
        },
    )


@permission_required("cosmetics_shop.add_category", raise_exception=True)
def create_categories(request):
    title = "Создание категории"
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
            "title": title,
            "form": form,
        },
    )


@permission_required("cosmetics_shop.add_groupproduct", raise_exception=True)
def create_groups(request):
    title = "Создание группы"
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
            "title": title,
            "form": form,
        },
    )


@permission_required("cosmetics_shop.add_brand", raise_exception=True)
def create_brands(request):
    title = "Создание бренда"
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
            "title": title,
            "form": form,
        },
    )


@permission_required("cosmetics_shop.add_tag", raise_exception=True)
def create_tags(request):
    title = "Создание тега"
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
            "title": title,
            "form": form,
        },
    )


@require_POST
@permission_required("cosmetics_shop.delete_tag", raise_exception=True)
def delete_tags(request):
    tag_id = request.POST.get("id")
    tag = get_object_or_404(Tag, id=tag_id)
    tag.delete()
    return redirect("tags_list")


@require_POST
@permission_required("cosmetics_shop.delete_category", raise_exception=True)
def delete_categories(request):
    category_id = request.POST.get("id")
    category = get_object_or_404(Category, id=category_id)
    category.delete()
    return redirect("categories_list")


@require_POST
@permission_required("cosmetics_shop.delete_groupproduct", raise_exception=True)
def delete_groups(request):
    group_id = request.POST.get("id")
    group = get_object_or_404(GroupProduct, id=group_id)
    group.delete()
    return redirect("groups_list")


@require_POST
@permission_required("cosmetics_shop.delete_brand", raise_exception=True)
def delete_brands(request):
    brand_id = request.POST.get("id")
    brand = get_object_or_404(Brand, id=brand_id)
    brand.delete()
    return redirect("brands_list")


@permission_required("cosmetics_shop.change_category", raise_exception=True)
def edit_categories(request, pk):
    category = get_object_or_404(Category, id=pk)
    title = f"Изменение категории: {category.name}"

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
            "title": title,
        },
    )


@permission_required("cosmetics_shop.change_groupproduct", raise_exception=True)
def edit_groups(request, pk):
    group = get_object_or_404(GroupProduct, id=pk)
    title = f"Изменение группы: {group.name}"

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
            "title": title,
        },
    )


@permission_required("cosmetics_shop.change_brand", raise_exception=True)
def edit_brands(request, pk):
    brand = get_object_or_404(Brand, id=pk)
    title = f"Изменение бренда: {brand.name}"
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
            "title": title,
        },
    )


@permission_required("cosmetics_shop.change_tag", raise_exception=True)
def edit_tags(request, pk):
    tag = get_object_or_404(Tag, id=pk)
    title = f"Изменение тега: {tag.name}"

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
            "title": title,
        },
    )
