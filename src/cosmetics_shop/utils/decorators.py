import logging
from functools import wraps

from django.contrib import messages
from django.shortcuts import redirect

from cosmetics_shop.utils.cart_utils import get_cart

logger = logging.getLogger(__name__)


def cart_required(view_func):
    """Decorator for checking that the basket is not empty"""

    @wraps(view_func)
    def wrapped_view(request, *args, **kwargs):
        cart = get_cart(request)

        if not cart or not cart.cart_items.exists():
            logger.warning(
                f"Empty cart access: user_id={getattr(request.user, 'id', None)}"
            )
            messages.error(
                request,
                "Ваша корзина пуста. Добавьте товары для оформления заказа.",
            )
            return redirect("cart")

        return view_func(request, *args, **kwargs)

    return wrapped_view


def order_session_required(view_func):
    """Decorator for checking if an order is in a session"""

    @wraps(view_func)
    def wrapped_view(request, *args, **kwargs):
        order_id = request.session.get("order_id")

        if not order_id:
            logger.warning("Order access without session order_id")
            messages.warning(request, "Заказ не найден.")
            return redirect("cart")

        from ..models import Order

        try:
            Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            logger.error(f"Invalid order in session: order_id={order_id}")
            messages.error(request, "Заказ не найден")

            if "order_id" in request.session:
                del request.session["order_id"]
                return redirect("cart")

        return view_func(request, *args, **kwargs)

    return wrapped_view
