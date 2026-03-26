from django.http import HttpRequest, HttpResponse
from django.shortcuts import render


def payment_and_delivery(request: HttpRequest) -> HttpResponse:
    return render(request, "cosmetics_shop/static_pages/payment_and_delivery_page.html")


def privacy_policy(request: HttpRequest) -> HttpResponse:
    return render(request, "cosmetics_shop/static_pages/privacy_policy.html")


def page_not_found(request: HttpRequest, exception: Exception) -> HttpResponse:
    return render(
        request, "cosmetics_shop/static_pages/404_page_not_found.html", status=404
    )
