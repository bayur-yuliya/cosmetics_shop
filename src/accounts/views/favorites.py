from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import HttpResponse
from django.shortcuts import render, redirect

from cosmetics_shop.models import Favorite
from utils.custom_types import AuthenticatedRequest


@login_required
def favorites(request: AuthenticatedRequest) -> HttpResponse:
    products = Favorite.objects.filter(user=request.user)

    paginator = Paginator(products, 20)
    page_number = request.GET.get("page")
    page = paginator.get_page(page_number)

    return render(
        request,
        "accounts/favorites.html",
        {
            "title": "Избранное",
            "products": page,
            "is_favorite": True,
        },
    )


@login_required
def remove_from_favorites(
    request: AuthenticatedRequest, product_id: int
) -> HttpResponse:
    Favorite.objects.filter(user=request.user, product_id=product_id).delete()
    return redirect("favorites")
