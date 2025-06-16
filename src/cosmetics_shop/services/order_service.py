from django.db import transaction

from cosmetics_shop.models import Cart, CartItem, Order, OrderItem


def create_order_from_cart(user):
    try:
        cart = Cart.objects.get(user=user)
        cart_items = CartItem.objects.filter(cart=cart)

        if not cart_items.exists():
            return None

        with transaction.atomic():

            order = Order.objects.create(user=user)

            order_items = []
            total_price = 0
            for item in cart_items:
                item_price = item.product.price
                total = item_price * item.quantity
                total_price += total

                order_items.append(OrderItem(
                    order=order,
                    product=item.product.name,
                    price=item_price,
                    quantity=item.quantity
                ))

            OrderItem.objects.bulk_create(order_items)

            order.total_price = total_price
            order.save()

            cart_items.delete()

            return order

    except Cart.DoesNotExist:
        return None
