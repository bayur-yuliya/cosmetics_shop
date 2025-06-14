from django.db import transaction

from cosmetics_shop.models import Card, CardItem, Order, OrderItem


def create_order_from_cart(user):
    try:
        card = Card.objects.get(user=user)
        card_items = CardItem.objects.filter(card=card)

        if not card_items.exists():
            return None

        with transaction.atomic():

            order = Order.objects.create(user=user)

            order_items = []
            total_price = 0
            for item in card_items:
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

            card_items.delete()

            return order

    except Card.DoesNotExist:
        return None
