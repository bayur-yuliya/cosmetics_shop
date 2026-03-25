import logging
from decimal import Decimal

from django.db.models import F, Sum
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_POST

from cosmetics_shop.models import Favorite, Product
from cosmetics_shop.services.cart_services import (
    add_product_to_cart,
    remove_product_from_cart,
)
from cosmetics_shop.utils.cart_utils import get_or_create_cart

logger = logging.getLogger(__name__)


@require_POST
def toggle_favorite(request: HttpRequest) -> HttpResponse:
    product_id = int(request.POST.get("product_id"))

    logger.debug(
        f"Toggle favorite: product_id={product_id},"
        f" user_id={getattr(request.user, 'id', None)}"
    )

    product = get_object_or_404(Product, id=product_id)
    message = None
    if request.user.is_authenticated:
        favorite = Favorite.objects.filter(user=request.user, product=product)

        if favorite.exists():
            favorite.delete()
            logger.info(
                f"Removed from favorites: user_id={request.user.id},"
                f" product_id={product_id}"
            )
            in_favorites = False
        else:
            Favorite.objects.get_or_create(user=request.user, product=product)
            logger.info(
                f"Added to favorites: user_id={request.user.id},"
                f" product_id={product_id}"
            )
            in_favorites = True
    else:
        logger.warning("Anonymous user tried to add favorite")
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
        logger.warning("Add to cart without product_code")
        return JsonResponse({"success": False, "error": "No product code"}, status=400)

    try:
        cart = get_or_create_cart(request)
        logger.debug(f"Add to cart: cart_id={cart.id}, product_code={product_code}")
        add_product_to_cart(cart, product_code=int(product_code))
        logger.info(
            f"Product added to cart: cart_id={cart.id}, product_code={product_code}"
        )
        return get_cart_status_response(cart, product_code)

    except Product.DoesNotExist:
        logger.warning(f"Product not found: product_code={product_code}")
        return JsonResponse(
            {"success": False, "error": "Product not found"}, status=404
        )


@require_POST
def cart_remove(request: HttpRequest) -> HttpResponse:
    product_code = request.POST.get("product_code")
    if not product_code:
        logger.warning("Remove from cart without product_code")
        return JsonResponse({"success": False, "error": "No product code"}, status=400)

    try:
        cart = get_or_create_cart(request)
        logger.debug(
            f"Remove from cart: cart_id={cart.id}, product_code={product_code}"
        )
        remove_product_from_cart(cart, int(product_code))
        logger.info(
            f"Product removed from cart: cart_id={cart.id}, product_code={product_code}"
        )
        return get_cart_status_response(cart, product_code)

    except Exception as e:
        logger.exception(
            f"Cart remove error: product_code={product_code}, error={str(e)}"
        )
        return JsonResponse({"success": False, "error": str(e)}, status=500)


def get_cart_status_response(cart, product_code):
    cart_items = cart.cart_items.select_related("product")

    total_count = cart_items.aggregate(total=Sum("quantity"))["total"] or 0

    total_price = cart_items.aggregate(total=Sum(F("quantity") * F("product__price")))[
        "total"
    ] or Decimal("0.00")

    current_item = cart_items.filter(product__code=product_code).first()

    product_qty = current_item.quantity if current_item else 0
    product_price = current_item.product.price if current_item else 0

    data = {
        "success": True,
        "count": total_count,
        "product_count": product_qty,
        "product_total_price": product_qty * product_price,
        "total_price": float(total_price),
        "product_code": product_code,
        "message": None,
        "is_max_quantity": current_item.product.stock == product_qty,
    }

    if current_item and current_item.quantity == current_item.product.stock:
        data["message"] = {"level": "error", "text": "Это последний товар"}

    return JsonResponse(data)
