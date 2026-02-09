from django.http import HttpRequest, HttpResponse
from django.shortcuts import render


def payment_and_delivery(request: HttpRequest) -> HttpResponse:
    return render(request, "cosmetics_shop/payment_and_delivery_page.html")


def page_not_found(request: HttpRequest, exception: Exception) -> HttpResponse:
    return render(request, "cosmetics_shop/404_page_not_found.html", status=404)
