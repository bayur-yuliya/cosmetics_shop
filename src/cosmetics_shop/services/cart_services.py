from django.contrib.auth.models import User

from cosmetics_shop.models import Cart, Product, CartItem


def get_or_create_cart(user):
    user = User.objects.get(username=user)
    cart, _ = Cart.objects.get_or_create(user=user)
    return cart


def get_cart_item(user, product_id):
    user = User.objects.get(username=user)
    product = Product.objects.get(id=product_id)
    cart, _ = Cart.objects.get_or_create(user=user)
    item, created = CartItem.objects.get_or_create(cart=cart, product=product)
    return item


def add_product_to_cart(user, product_id):
    item = get_cart_item(user, product_id)
    item.quantity += 1
    item.save()


def remove_product_to_cart(user, product_id):
    try:
        item = get_cart_item(user, product_id)
        item.quantity -= 1
        if item.quantity <= 0:
            item.delete()
        else:
            item.save()
    except CartItem.DoesNotExist:
        pass


def delete_product_to_cart(user, product_id):
    try:
        item = get_cart_item(user, product_id)
        item.delete()
    except CartItem.DoesNotExist:
        pass


def calculate_cart_total(user):
    cart = get_or_create_cart(user)
    return sum(item.product.price * item.quantity for item in cart.cartitem_set.all())
