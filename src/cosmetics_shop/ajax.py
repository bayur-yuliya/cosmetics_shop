from django.http import JsonResponse, HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_POST

from cosmetics_shop.models import Product, Favorite
from cosmetics_shop.services.cart_services import (
    add_product_to_cart,
    remove_product_from_cart,
    get_cart_status_response,
)
from cosmetics_shop.utils.cart_utils import get_or_create_cart


@require_POST
def toggle_favorite(request: HttpRequest) -> HttpResponse:
    product_id = request.POST.get("product_id")
    product = get_object_or_404(Product, id=product_id)
    message = None
    if request.user.is_authenticated:
        favorite = Favorite.objects.filter(user=request.user, product=product)

        if favorite.exists():
            favorite.delete()
            in_favorites = False
        else:
            Favorite.objects.get_or_create(user=request.user, product=product)
            in_favorites = True
    else:
        message = {
            "level": "warning",
            "text": "Требуется зарегистрироваться для добавления товара в избранное",
        }
        in_favorites = False

    return JsonResponse({"in_favorites": in_favorites, "message": message})


@require_POST
def add_to_cart(request: HttpRequest) -> HttpResponse:
    product_code = request.POST.get("product_code")
    if not product_code:
        return JsonResponse({"success": False, "error": "No product code"}, status=400)

    try:
        cart = get_or_create_cart(request)
        add_product_to_cart(cart, product_code=int(product_code))
        return get_cart_status_response(cart, product_code)

    except Product.DoesNotExist:
        return JsonResponse(
            {"success": False, "error": "Product not found"}, status=404
        )


@require_POST
def cart_remove(request: HttpRequest) -> HttpResponse:
    product_code = request.POST.get("product_code")
    if not product_code:
        return JsonResponse({"success": False, "error": "No product code"}, status=400)

    try:
        cart = get_or_create_cart(request)
        remove_product_from_cart(cart, int(product_code))
        return get_cart_status_response(cart, product_code)

    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=500)
