from cosmetics_shop.models import (
    Cart,
    CartItem,
    Order,
    OrderItem,
    DeliveryAddress,
    Client, Product,
)


def get_cart(request):
    if request.user.is_authenticated:
        cart, _ = Cart.objects.get_or_create(user=request.user)
    else:
        cart_id = request.session.get("cart_id")
        if cart_id:
            try:
                return Cart.objects.get(id=cart_id)
            except Cart.DoesNotExist:
                pass
        cart = Cart.objects.create()
        request.session["cart_id"] = cart.id
    return cart


def get_client(request):
    if request.user.is_authenticated:
        return Client.objects.get(user=request.user)
    else:
        client_id = request.session.get("client_id")
        return Client.objects.get(id=client_id)


def change_stock_product(product_id, count):
    product = Product.objects.get(id=product_id)
    if product.stock >= count:
        product.stock -= count
        product.save()
    else:
        raise ValueError("Товаров больше нет")


def create_order_from_cart(request, address_id):
    cart = get_cart(request)
    cart_items = CartItem.objects.select_related("product").filter(cart=cart)

    if not cart_items.exists():
        raise ValueError("Корзина пуста")

    try:
        client = get_client(request)
    except Client.DoesNotExist:
        raise ValueError("Клиент не найден")

    try:
        address = DeliveryAddress.objects.get(id=address_id, client=client)
    except DeliveryAddress.DoesNotExist:
        raise ValueError("Адрес не найден или не принадлежит клиенту")

    total_price = sum(item.product.price * item.quantity for item in cart_items)

    order = Order.objects.create(
        client=client,
        snapshot_name=client.full_name,
        snapshot_email=client.email,
        snapshot_phone=client.phone,
        snapshot_address=str(address),
        total_price=total_price,
    )

    order_items = [
        OrderItem(
            order=order,
            product=item.product.name,
            price=item.product.price,
            quantity=item.quantity,
        )
        for item in cart_items
    ]
    for item in cart_items:
        change_stock_product(item.product.id, item.quantity)
    OrderItem.objects.bulk_create(order_items)

    cart_items.delete()

    if not request.user.is_authenticated:
        request.session.pop("cart_id", None)

    return order
