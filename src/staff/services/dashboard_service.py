import datetime

from dateutil.relativedelta import relativedelta
from django.db.models import Avg, Sum

from cosmetics_shop.models import Order, Status


def number_of_orders_today():
    number_of_orders_today = (
        Order.objects.filter(
            created_at__gte=datetime.date.today(), status_log__status=Status.CLOSED
        )
        .distinct()
        .count()
    )

    return number_of_orders_today


def orders_per_month(month):
    one_month_ago = month - relativedelta(months=1)
    orders_per_month = Order.objects.filter(
        created_at__gte=one_month_ago, status_log__status=Status.CLOSED
    ).distinct()
    return orders_per_month


def number_of_orders_per_month(month):
    number_of_orders_per_month = orders_per_month(month).count()
    return number_of_orders_per_month


def summ_bill(month):
    orders = orders_per_month(month)
    if orders.aggregate(avg_bill=Sum("total_price"))["avg_bill"]:
        summ_bill = int(orders.aggregate(avg_bill=Sum("total_price"))["avg_bill"])
    else:
        summ_bill = 0
    return summ_bill


def average_bill(month):
    orders = orders_per_month(month)
    if orders.aggregate(avg_bill=Avg("total_price"))["avg_bill"]:
        average_bill = orders.aggregate(avg_bill=Avg("total_price"))["avg_bill"]
    else:
        average_bill = 0
    return average_bill
