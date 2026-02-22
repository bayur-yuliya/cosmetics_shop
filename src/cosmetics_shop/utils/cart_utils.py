from django.http import HttpRequest

from cosmetics_shop.models import Cart


def get_or_create_cart(request: HttpRequest) -> Cart:
    if request.user.is_authenticated:
        cart, _ = Cart.objects.get_or_create(user=request.user)
    else:
        session_key = request.session.session_key
        if session_key:
            cart, _ = Cart.objects.get_or_create(session_key=session_key)
        else:
            request.session.create()
            session_key = request.session.session_key
            cart = Cart.objects.create(session_key=session_key)
    return cart
