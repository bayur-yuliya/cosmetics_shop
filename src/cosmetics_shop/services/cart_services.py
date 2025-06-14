from django.contrib.auth.models import User

from cosmetics_shop.models import Card, Product, CardItem


def get_or_create_cart(user):
    user = User.objects.get(username=user)
    cart, _ = Card.objects.get_or_create(user=user)
    return cart


def get_cart_item(user, product_id):
    user = User.objects.get(username=user)
    product = Product.objects.get(id=product_id)
    cart, _ = Card.objects.get_or_create(user=user)
    item, created = CardItem.objects.get_or_create(card=cart, product=product)
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
    except CardItem.DoesNotExist:
        pass


def delete_product_to_cart(user, product_id):
    try:
        item = get_cart_item(user, product_id)
        item.delete()
    except CardItem.DoesNotExist:
        pass


def calculate_cart_total(user):
    cart = get_or_create_cart(user)
    return sum(item.product.price * item.quantity for item in cart.carditem_set.all())
