import datetime
from typing import Any

from django.contrib import messages
from django.contrib.auth.decorators import permission_required
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.auth.models import Group
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import OuterRef, Subquery, Count, QuerySet
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.decorators.http import require_POST

from accounts.models import CustomUser
from cosmetics_shop.models import (
    Product,
    Order,
    OrderItem,
    OrderStatusLog,
    Category,
    Tag,
    Favorite,
    GroupProduct,
    Brand,
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
from utils.custom_types import AuthenticatedRequest
from .services.dashboard_service import (
    number_of_completed_orders_today,
    number_of_orders_per_month,
    summ_bill,
    average_bill,
)
from .services.list_service import (
    BaseStaffCreateView,
    BaseStaffListView,
    BaseStaffChangeView,
    BaseStaffDeleteView,
)
from .services.permission_service import get_individually_assigned_permits


class StaffPermissionMixin(PermissionRequiredMixin):
    raise_exception = True


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
    groups: QuerySet[Group] = Group.objects.annotate(
        user_count=Count("user")
    ).prefetch_related("permissions")

    return render(
        request,
        "staff/permissions/groups_list.html",
        {"title": "Список групп разрешений", "groups": groups},
    )


@permission_required("staff.manage_permission", raise_exception=True)
def staff_group_edit(request: HttpRequest, pk: int) -> HttpResponse:
    group: Group | None = get_object_or_404(Group, pk=pk)
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
    user = get_object_or_404(CustomUser, pk=user_id)

    if request.method == "POST":
        selected_groups: list[str] | None = request.POST.getlist("groups")
        if selected_groups:
            selected_groups_id = [int(pk) for pk in selected_groups]
            user.groups.set(selected_groups_id)

        selected_permissions = request.POST.getlist("permissions")
        if selected_permissions:
            perms_id = [int(pk) for pk in selected_permissions]
            user.user_permissions.set(perms_id)
        return redirect("staff_list")

    all_groups = Group.objects.all()
    user_groups = user.groups.all()

    permissions = get_individually_assigned_permits()

    permissions_by_app: dict[str, Any] = {}
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
    products_list = (
        Product.objects.all()
        .order_by("-id")
        .filter(is_active=True)
        .select_related("brand")
    )

    form = ProductStuffFilterForm(request.GET or None)
    form_stock = FilterStockForm(request.GET or None)

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

    if form_stock.is_valid():
        min_stock = form_stock.cleaned_data["min_stock"]
        max_stock = form_stock.cleaned_data["max_stock"]
        if min_stock:
            products_list = products_list.filter(stock__gte=min_stock)
        if max_stock:
            products_list = products_list.filter(stock__lte=max_stock)

    paginator = Paginator(products_list, 20)
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
    product_id: str | None = request.POST.get("product_id")
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
def order_info(request: AuthenticatedRequest, order_code: int) -> HttpResponse:
    title = f"Заказ {order_code}"

    order: Order = get_object_or_404(Order, code=order_code)
    order_items: QuerySet[OrderItem] = OrderItem.objects.filter(order=order)

    if request.method == "POST":
        form = OrderStatusForm(request.POST, instance=order, user=request.user)
        if form.is_valid():
            last: OrderStatusLog | None = OrderStatusLog.objects.filter(
                order=order
            ).first()

            if last and (
                last.status != form.cleaned_data["status"]
                or last.comment != form.cleaned_data["comment"]
            ):
                with transaction.atomic():
                    OrderStatusLog.objects.create(
                        order=order,
                        changed_by=request.user,
                        status=form.cleaned_data["status"],
                        comment=form.cleaned_data["comment"],
                    )
                    form.save()
                    messages.success(request, "Статус успешно изменен")
            else:
                messages.success(request, "Статус не изменен")

            return redirect("order_info", order_code=order.code)

    form = OrderStatusForm(instance=order, user=request.user)
    order_status_log: QuerySet[OrderStatusLog] = OrderStatusLog.objects.filter(
        order=order
    )

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


# Category
class CategoryListView(BaseStaffListView):
    model = Category
    page_title = "Список категорий"
    permission_required = "cosmetics_shop.view_category"


class CategoryCreateView(BaseStaffCreateView):
    page_title = "Создание категории"
    model = Category
    form_class = CategoryForm
    permission_required = "cosmetics_shop.add_category"
    success_url = reverse_lazy("categories_list")


class CategoryChangeView(BaseStaffChangeView):
    page_title = "Изменение категории"
    model = Category
    form_class = CategoryForm
    permission_required = "cosmetics_shop.change_category"
    success_url = reverse_lazy("categories_list")


class CategoryDeleteView(BaseStaffDeleteView):
    model = Category
    permission_required = "cosmetics_shop.delete_category"
    success_url = reverse_lazy("categories_list")


# GroupProduct
class GroupProductListView(BaseStaffListView):
    model = GroupProduct
    page_title = "Список групп"
    permission_required = "cosmetics_shop.view_groupproduct"


class GroupProductCreateView(BaseStaffCreateView):
    page_title = "Создание группы"
    model = GroupProduct
    form_class = GroupProductForm
    permission_required = "cosmetics_shop.add_groupproduct"
    success_url = reverse_lazy("groups_list")


class GroupProductChangeView(BaseStaffChangeView):
    page_title = "Изменение группы"
    model = GroupProduct
    form_class = GroupProductForm
    permission_required = "cosmetics_shop.add_groupproduct"
    success_url = reverse_lazy("groups_list")


class GroupProductDeleteView(BaseStaffDeleteView):
    model = GroupProduct
    permission_required = "cosmetics_shop.delete_groupproduct"
    success_url = reverse_lazy("groups_list")


# Brand
class BrandListView(BaseStaffListView):
    model = Brand
    page_title = "Список брендов"
    permission_required = "cosmetics_shop.view_brand"


class BrandCreateView(BaseStaffCreateView):
    page_title = "Создание бренда"
    model = Brand
    form_class = BrandForm
    permission_required = "cosmetics_shop.add_brand"
    success_url = reverse_lazy("brands_list")


class BrandChangeView(BaseStaffChangeView):
    page_title = "Изменение бренда"
    model = Brand
    form_class = BrandForm
    permission_required = "cosmetics_shop.change_brand"
    success_url = reverse_lazy("brands_list")


class BrandDeleteView(BaseStaffDeleteView):
    model = Brand
    permission_required = "cosmetics_shop.delete_brand"
    success_url = reverse_lazy("brands_list")


# Tag
class TagListView(BaseStaffListView):
    model = Tag
    page_title = "Список тегов"
    permission_required = "cosmetics_shop.view_tag"


class TagCreateView(BaseStaffCreateView):
    page_title = "Создание тега"
    model = Tag
    form_class = TagForm
    permission_required = "cosmetics_shop.add_tag"
    success_url = reverse_lazy("tags_list")


class TagChangeView(BaseStaffChangeView):
    page_title = "Изменение тега"
    model = Tag
    form_class = TagForm
    permission_required = "cosmetics_shop.change_tag"
    success_url = reverse_lazy("tags_list")


class TagDeleteView(BaseStaffDeleteView):
    model = Tag
    permission_required = "cosmetics_shop.delete_tag"
    success_url = reverse_lazy("tags_list")
