from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST

from cosmetics_shop.models import Product, Order, OrderItem, OrderStatusLog
from stuff.forms import ProductForm, OrderStatusForm
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
    return render(
        request,
        "stuff/products.html",
        {
            "title": title,
            "products": products,
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
        form = ProductForm(request.POST)
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
        form = ProductForm(request.POST, instance=product)
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
    orders_list = Order.objects.all()
    if request.method == "POST":
        form = OrderStatusForm(request.POST)
        if form.is_valid():
            orders_list = Order.objects.filter(status=form.cleaned_data["status"])
            return render(
                request,
                "stuff/orders.html",
                {
                    "title": title,
                    "orders": orders_list,
                    "form": form,
                },
            )
    else:
        form = OrderStatusForm()
    return render(
        request,
        "stuff/orders.html",
        {
            "title": title,
            "orders": orders_list,
            "form": form,
        },
    )


@staff_member_required
def order_info(request, order_id):
    title = f"Заказ {order_id}"
    order = Order.objects.get(id=order_id)
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
            return redirect("order_info", order_id=order.id)
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
