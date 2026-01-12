from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_POST

from cosmetics_shop.models import Product, Favorite, CartItem
from cosmetics_shop.services.cart_services import (
    add_product_to_cart,
    get_or_create_cart_for_session,
    get_or_create_cart,
    remove_product_from_cart,
    calculate_cart_total,
)


@require_POST
def toggle_favorite(request):
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
def add_to_cart(request):
    try:
        product_code = request.POST.get("product_code")

        if not product_code:
            return JsonResponse({"success": False, "error": "No product code"})

        if request.user.is_authenticated:
            cart = get_or_create_cart(request)
        else:
            cart = get_or_create_cart_for_session(request)

        add_product_to_cart(cart, product_code=product_code)

        cart_items = CartItem.objects.select_related("product").filter(cart=cart)
        count = sum(item.quantity for item in cart_items)

        product_count = cart_items.filter(product__code=product_code).first()

        total_price = calculate_cart_total(cart)

        product_total_price = product_count.quantity * product_count.product.price / 100

        message = None
        if product_count.quantity == product_count.product.stock:
            message = {
                "level": "error",
                "text": "Это последний товар",
            }

        return JsonResponse(
            {
                "success": True,
                "count": count,
                "product_count": product_count.quantity,
                "total_price": float(total_price),
                "product_total_price": product_total_price,
                "product_code": product_code,
                "message": message,
            }
        )

    except Product.DoesNotExist:
        return JsonResponse({"success": False, "error": "Product not found"})
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)})


@require_POST
def cart_remove(request):
    product_code = request.POST.get("product_code")

    if request.user.is_authenticated:
        cart = get_or_create_cart(request)
    else:
        cart = get_or_create_cart_for_session(request)

    remove_product_from_cart(cart, product_code)

    cart_items = CartItem.objects.select_related("product").filter(cart=cart)
    count = sum(item.quantity for item in cart_items)

    product_count = cart_items.filter(product__code=product_code).first()
    total_price = calculate_cart_total(cart)

    product_total_price = product_count.quantity * product_count.product.price / 100

    return JsonResponse(
        {
            "success": True,
            "count": count,
            "product_count": product_count.quantity,
            "product_total_price": product_total_price,
            "total_price": float(total_price),
            "product_code": product_code,
        }
    )
