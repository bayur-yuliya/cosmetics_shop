from cosmetics_shop.models import CartItem
from cosmetics_shop.services.cart_services import get_or_create_cart


def cart_item_count(request):
    cart = get_or_create_cart(request)
    cart_items = CartItem.objects.filter(cart=cart)
    count = sum(item.quantity for item in cart_items)
    return {"cart_item_count": count}
