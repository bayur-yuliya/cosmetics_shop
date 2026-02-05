import datetime
from typing import Optional, Dict, List, cast

from django.contrib import messages
from django.contrib.auth.decorators import permission_required
from django.contrib.auth.models import Group
from django.core.paginator import Paginator
from django.db.models import OuterRef, Subquery, Count, QuerySet
from django.http import HttpRequest, HttpResponse, QueryDict
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
    AdminCreateUserForm,
)
from .services.dashboard_service import (
    number_of_completed_orders_today,
    number_of_orders_per_month,
    summ_bill,
    average_bill,
)
from .services.list_service import get_permissions
from .services.permission_service import get_individually_assigned_permits


@permission_required("staff.dashboard_view", raise_exception=False)
def index(request: HttpRequest) -> HttpResponse:
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
            "title": "Главная страница",
            "number_of_completed_orders_today": completed_orders_today,
            "number_of_orders_per_month": orders_per_month,
            "summ_bill": summ,
            "average_bill": average,
            "max_favorite": max_favorite,
            "years": years,
            "current_year": current_year,
        },
    )


@permission_required("staff.manage_permission", raise_exception=True)
def staff_group_list(request: HttpRequest) -> HttpResponse:
    groups = Group.objects.annotate(user_count=Count("user")).prefetch_related(
        "permissions"
    )

    return render(
        request,
        "staff/permissions/groups_list.html",
        {"title": "Список групп разрешений", "groups": groups},
    )


@permission_required("staff.manage_permission", raise_exception=True)
def staff_group_edit(request: HttpRequest, pk: Optional[int] = None) -> HttpResponse:
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
def staff_list(request: HttpRequest) -> HttpResponse:
    staffs: QuerySet[CustomUser] = CustomUser.objects.filter(
        is_staff=True
    ).prefetch_related("groups", "user_permissions")
    return render(
        request,
        "staff/permissions/staff_list.html",
        {"title": "Страница сотрудников", "staffs": staffs},
    )


@permission_required("staff.manage_permission", raise_exception=True)
def edit_staff_permissions(request: HttpRequest, user_id: int) -> HttpResponse:
    user = get_object_or_404(CustomUser, id=user_id)

    if request.method == "POST":
        selected_groups: Optional[List[str]] = request.POST.getlist("groups")
        if selected_groups:
            user.groups.clear()
            for group_id in selected_groups:
                group = Group.objects.get(id=group_id)
                user.groups.add(group)

            selected_permissions = request.POST.getlist("permissions")
            perms_id = [int(pk) for pk in selected_permissions]
            user.user_permissions.set(perms_id)
            return redirect("staff_list")

    all_groups = Group.objects.all()
    user_groups = user.groups.all()

    permissions = get_individually_assigned_permits()

    permissions_by_app: Dict = {}
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


@permission_required("staff.manage_permission", raise_exception=True)
def create_staff_user(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        form = AdminCreateUserForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("main_page")
    form = AdminCreateUserForm()
    return render(
        request,
        "staff/create_staff_user.html",
        {"form": form, "title": "Отправка приглашения сотруднику"},
    )


@permission_required("cosmetics_shop.view_product", raise_exception=True)
def products(request: HttpRequest) -> HttpResponse:
    products = (
        Product.objects.all()
        .order_by("-id")
        .filter(is_active=True)
        .select_related("brand")
    )

    query_params: Optional[QueryDict] = request.GET.copy()
    if query_params:
        for key in list(query_params.keys()):
            value = query_params.get(key, "")
            if not value or not value.strip():
                query_params.pop(key)
        if request.GET.urlencode() != query_params.urlencode():
            return redirect(f"{request.path}?{query_params.urlencode()}")

    form = ProductStuffFilterForm(request.GET or None)
    form_stock = FilterStockForm(request.GET or None)

    if form.is_valid():
        name = form.cleaned_data["name"]
        code = form.cleaned_data["code"]
        brand = form.cleaned_data["brand"]
        min_price = form.cleaned_data["min_price"]
        max_price = form.cleaned_data["max_price"]

        if name:
            products = products.filter(name__icontains=name)
        if brand:
            products = products.filter(brand__name__icontains=brand)
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
    page = paginator.get_page(page_number)

    return render(
        request,
        "staff/products.html",
        {
            "title": "Товары",
            "products": page,
            "form": form,
            "form_stock": form_stock,
        },
    )


@permission_required("cosmetics_shop.view_product", raise_exception=True)
def product_card(request: HttpRequest, product_id: int) -> HttpResponse:
    product = get_object_or_404(Product, pk=product_id)
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
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect("products")
    form = ProductForm()

    return render(
        request,
        "staff/create_product.html",
        {
            "title": "Создание карточки товара",
            "form": form,
        },
    )


@permission_required("cosmetics_shop.change_product", raise_exception=True)
def edit_products(request: HttpRequest, product_id: int) -> HttpResponse:
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
            "title": "Изменение товара",
            "form": form,
            "product": product,
        },
    )


@require_POST
@permission_required("cosmetics_shop.delete_product", raise_exception=True)
def delete_product(request: HttpRequest) -> HttpResponse:
    product_id: Optional[str] = request.POST.get("product_id")
    if product_id:
        product: Product = get_object_or_404(Product, id=product_id)
        product.is_active = False
        product.save()
    else:
        messages.error(request, "Не удалось удалить товар")
    return redirect("products")


@permission_required("cosmetics_shop.view_order", raise_exception=True)
def orders(request: HttpRequest) -> HttpResponse:
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
                    "title": "Список заказов",
                    "form": form,
                    "status": latest_statuses,
                },
            )
    else:
        form = OrderStatusForm()

    paginator = Paginator(latest_statuses, 20)
    page_number = request.GET.get("page")
    page = paginator.get_page(page_number)

    return render(
        request,
        "staff/orders.html",
        {
            "title": "Список заказов",
            "form": form,
            "status": page,
        },
    )


@permission_required("cosmetics_shop.view_order", raise_exception=True)
def order_info(request: HttpRequest, order_code: int) -> HttpResponse:
    title = f"Заказ {order_code}"

    order: Order = get_object_or_404(Order, code=order_code)
    order_items: QuerySet[OrderItem] = OrderItem.objects.filter(order=order)
    user = cast(CustomUser, request.user)

    if request.method == "POST":
        form = OrderStatusForm(request.POST, instance=order, user=user)
        if form.is_valid():
            last: Optional[OrderStatusLog] = OrderStatusLog.objects.filter(
                order=order
            ).first()

            if last and (
                last.status != form.cleaned_data["status"]
                or last.comment != form.cleaned_data["comment"]
            ):
                OrderStatusLog.objects.create(
                    order=order,
                    changed_by=user,
                    status=form.cleaned_data["status"],
                    comment=form.cleaned_data["comment"],
                )
                form.save()
                messages.success(request, "Статус успешно изменен")
            else:
                messages.success(request, "Статус установлен")

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
def brands_list(request: HttpRequest) -> HttpResponse:
    objects = Brand.objects.all()

    permissions = get_permissions(request, objects)

    paginator = Paginator(objects, 20)
    page_number = request.GET.get("page")
    page = paginator.get_page(page_number)

    return render(
        request,
        "staff/lists_page.html",
        {
            "title": "Список брендов",
            "objects": page,
            "permissions": permissions,
        },
    )


@permission_required("cosmetics_shop.view_category", raise_exception=True)
def categories_list(request: HttpRequest) -> HttpResponse:
    objects: QuerySet[Category] = Category.objects.all()

    permissions = get_permissions(request, objects)

    paginator = Paginator(objects, 20)
    page_number = request.GET.get("page")
    page = paginator.get_page(page_number)

    return render(
        request,
        "staff/lists_page.html",
        {
            "objects": page,
            "title": "Список категорий",
            "permissions": permissions,
        },
    )


@permission_required("cosmetics_shop.view_tag", raise_exception=True)
def tags_list(request: HttpRequest) -> HttpResponse:
    objects: QuerySet[Tag] = Tag.objects.all()

    permissions = get_permissions(request, objects)

    paginator = Paginator(objects, 20)
    page_number = request.GET.get("page")
    page = paginator.get_page(page_number)

    return render(
        request,
        "staff/lists_page.html",
        {
            "title": "Список тегов",
            "objects": page,
            "permissions": permissions,
        },
    )


@permission_required("cosmetics_shop.view_groupproduct", raise_exception=True)
def groups_list(request: HttpRequest) -> HttpResponse:
    objects: QuerySet[GroupProduct] = GroupProduct.objects.all()
    permissions = get_permissions(request, objects)

    paginator = Paginator(objects, 20)
    page_number = request.GET.get("page")
    page = paginator.get_page(page_number)

    return render(
        request,
        "staff/lists_page.html",
        {
            "title": "Список групп",
            "objects": page,
            "permissions": permissions,
        },
    )


@permission_required("cosmetics_shop.add_category", raise_exception=True)
def create_categories(request: HttpRequest) -> HttpResponse:
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
            "title": "Создание категории",
            "form": form,
        },
    )


@permission_required("cosmetics_shop.add_groupproduct", raise_exception=True)
def create_groups(request: HttpRequest) -> HttpResponse:
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
            "title": "Создание группы",
            "form": form,
        },
    )


@permission_required("cosmetics_shop.add_brand", raise_exception=True)
def create_brands(request: HttpRequest) -> HttpResponse:
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
            "title": "Создание бренда",
            "form": form,
        },
    )


@permission_required("cosmetics_shop.add_tag", raise_exception=True)
def create_tags(request: HttpRequest) -> HttpResponse:
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
            "title": "Создание тега",
            "form": form,
        },
    )


@require_POST
@permission_required("cosmetics_shop.delete_tag", raise_exception=True)
def delete_tags(request: HttpRequest) -> HttpResponse:
    tag_id = request.POST.get("id")
    if tag_id is not None:
        tag = get_object_or_404(Tag, id=tag_id)
        tag.delete()
    else:
        messages.error(request, "Не удалось удалить тэг")
    return redirect("tags_list")


@require_POST
@permission_required("cosmetics_shop.delete_category", raise_exception=True)
def delete_categories(request: HttpRequest) -> HttpResponse:
    category_id = request.POST.get("id")
    if category_id is not None:
        category = get_object_or_404(Category, id=category_id)
        category.delete()
    else:
        messages.error(request, "Не удалось удалить категорию")
    return redirect("categories_list")


@require_POST
@permission_required("cosmetics_shop.delete_groupproduct", raise_exception=True)
def delete_groups(request: HttpRequest) -> HttpResponse:
    group_id = request.POST.get("id")
    if group_id is not None:
        group = get_object_or_404(GroupProduct, id=group_id)
        group.delete()
    else:
        messages.error(request, "Не удалось удалить группу")
    return redirect("groups_list")


@require_POST
@permission_required("cosmetics_shop.delete_brand", raise_exception=True)
def delete_brands(request: HttpRequest) -> HttpResponse:
    brand_id = request.POST.get("id")
    if brand_id is not None:
        brand = get_object_or_404(Brand, id=brand_id)
        brand.delete()
    else:
        messages.error(request, "Не удалось удалить бренд")
    return redirect("brands_list")


@permission_required("cosmetics_shop.change_category", raise_exception=True)
def edit_categories(request: HttpRequest, pk: int) -> HttpResponse:
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
def edit_groups(request: HttpRequest, pk: int) -> HttpResponse:
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
def edit_brands(request: HttpRequest, pk: int) -> HttpResponse:
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
def edit_tags(request: HttpRequest, pk: int) -> HttpResponse:
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
