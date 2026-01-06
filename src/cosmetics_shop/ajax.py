from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_POST

from cosmetics_shop.models import Product, Favorite, CartItem
from cosmetics_shop.services.cart_services import (
    add_product_to_cart,
    get_or_create_cart_for_session,
    get_or_create_cart,
    remove_product_from_cart,
)


@login_required
@require_POST
def toggle_favorite(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    favorite = Favorite.objects.filter(user=request.user, product=product)

    if favorite.exists():
        favorite.delete()
        in_favorites = False
    else:
        Favorite.objects.get_or_create(user=request.user, product=product)
        in_favorites = True

    return JsonResponse({"in_favorites": in_favorites})


@require_POST
def add_to_cart(request, product_code):
    try:
        if not product_code:
            return JsonResponse({"success": False, "error": "No product code"})

        if request.user.is_authenticated:
            add_product_to_cart(request, product_code=product_code)
            cart = get_or_create_cart(request)
        else:
            cart = get_or_create_cart_for_session(request)
            product = Product.objects.get(code=product_code)

            item, created = CartItem.objects.get_or_create(cart=cart, product=product)

            item.quantity += 1
            item.save()

        cart_items = CartItem.objects.select_related("product").filter(cart=cart)
        count = sum(item.quantity for item in cart_items)

        product_count = cart_items.filter(product__code=product_code).first()

        total_price = (
            sum(item.product.price * item.quantity for item in cart_items) / 100
        )

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
def cart_remove(request, product_code):
    remove_product_from_cart(request, product_code)

    if request.user.is_authenticated:
        cart = get_or_create_cart(request)
    else:
        cart = get_or_create_cart_for_session(request)

    cart_items = CartItem.objects.select_related("product").filter(cart=cart)
    count = sum(item.quantity for item in cart_items)

    product_count = cart_items.filter(product__code=product_code).first()
    total_price = sum(item.product.price * item.quantity for item in cart_items) / 100

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
