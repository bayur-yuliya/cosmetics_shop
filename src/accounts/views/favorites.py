from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import redirect, render

from cosmetics_shop.models import Favorite
from utils.custom_types import AuthenticatedRequest
from utils.helper_function import get_paginator_page


@login_required
def favorites(request: AuthenticatedRequest) -> HttpResponse:
    products = Favorite.objects.filter(user=request.user)
    page = get_paginator_page(request, products)

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
