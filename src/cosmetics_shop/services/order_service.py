from cosmetics_shop.models import Cart, CartItem, Order, OrderItem, DeliveryAddress, Client


def create_order_from_cart(user, address_id):

    client = Client.objects.get(user=user)
    address = DeliveryAddress.objects.get(id=address_id)

    cart = Cart.objects.get(user=user)
    cart_items = CartItem.objects.filter(cart=cart)
    total_price = sum(item.product.price * item.quantity for item in cart_items)

    order = Order.objects.create(
        client=client,
        snapshot_name=client.full_name,
        snapshot_email=client.email,
        snapshot_phone=client.phone,
        snapshot_address=str(address),
        total_price=total_price
    )

    for item in cart_items:
        OrderItem.objects.create(
            order=order,
            product=item.product.name,
            price=item.product.price,
            quantity=item.quantity
        )

    cart_items.delete()

    return order
