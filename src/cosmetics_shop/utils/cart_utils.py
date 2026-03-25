import logging

from django.http import HttpRequest

from cosmetics_shop.models import Cart

logger = logging.getLogger(__name__)


def get_cart(request: HttpRequest) -> Cart | None:
    if request.user.is_authenticated:
        cart = Cart.objects.filter(user=request.user).first()
        logger.debug(f"Get cart (user): user_id={request.user.id}, found={bool(cart)}")
        return cart

    session_key = request.session.session_key

    if session_key:
        cart = Cart.objects.filter(session_key=session_key).first()
        logger.debug(f"Get cart (session): session_key={session_key}")
        return cart

    logger.debug("No cart found")

    return None


def get_or_create_cart(request: HttpRequest) -> Cart:
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
        logger.debug(
            f"Cart get/create (user): user_id={request.user.id}, created={created}"
        )
    else:
        session_key = request.session.session_key

        if not session_key:
            request.session.create()
            session_key = request.session.session_key
            logger.debug(f"Session created: session_key={session_key}")

        cart, created = Cart.objects.get_or_create(session_key=session_key)

        logger.debug(
            f"Cart get/create (session): session_key={session_key}, created={created}"
        )

    return cart
