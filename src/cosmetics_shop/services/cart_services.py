from django.contrib import messages
from django.contrib.auth.models import User

from cosmetics_shop.models import Cart, Product, CartItem, Client


def get_or_create_cart(request):
    if request.user.is_authenticated:
        cart, _ = Cart.objects.get_or_create(user=request.user)
    else:
        cart_id = request.session.get("cart_id")
        if cart_id:
            try:
                cart = Cart.objects.get(id=cart_id)
            except Cart.DoesNotExist:
                cart = Cart.objects.create()
                request.session["cart_id"] = cart.id
        else:
            cart = Cart.objects.create()
            request.session["cart_id"] = cart.id
    return cart


def get_cart_item(user, product_code):
    user = User.objects.get(username=user)
    product = Product.objects.get(code=product_code)
    cart, _ = Cart.objects.get_or_create(user=user)
    item, created = CartItem.objects.get_or_create(cart=cart, product=product)
    return item


def add_product_to_cart(request, product_code):
    cart = get_or_create_cart(request)
    product = Product.objects.get(code=product_code)

    item, created = CartItem.objects.get_or_create(cart=cart, product=product)
    if item.quantity < item.product.stock:
        item.quantity += 1
    item.save()


def remove_product_from_cart(request, product_code):
    cart = get_or_create_cart(request)
    product = Product.objects.get(code=product_code)

    try:
        item = CartItem.objects.get(cart=cart, product=product)
        if item.quantity > 1:
            item.quantity -= 1
            item.save()
    except CartItem.DoesNotExist:
        pass


def delete_product_from_cart(request, product_id):
    cart = get_or_create_cart(request)
    product = Product.objects.get(id=product_id)
    CartItem.objects.filter(cart=cart, product=product).delete()
    messages.success(request, "Товар успешно удален")


def delete_cart(request):
    cart = get_or_create_cart(request)
    CartItem.objects.filter(cart=cart).delete()
    messages.success(request, "Корзина очищена")


def calculate_cart_total(user):
    cart = get_or_create_cart(user)
    return sum(item.product.price * item.quantity for item in cart.cartitem_set.all())


def get_or_create_cart_for_session(request):
    cart_id = request.session.get("cart_id")

    if cart_id:
        try:
            return Cart.objects.get(id=cart_id)
        except Cart.DoesNotExist:
            del request.session["cart_id"]

    cart = Cart.objects.create()
    request.session["cart_id"] = cart.id
    return cart


def get_or_create_session_client(request, form=None):
    client_id = request.session.get("client_id")

    if client_id:
        try:
            return Client.objects.get(id=client_id)
        except Client.DoesNotExist:
            del request.session["client_id"]

    if form:
        client = Client.objects.create(
            first_name=form.cleaned_data["first_name"],
            last_name=form.cleaned_data["last_name"],
            phone=form.cleaned_data["phone"],
            is_active=False,
        )
        request.session["client_id"] = client.id
        return client

    return None


def clear_cart_after_order(request):
    cart = get_or_create_cart(request)
    cart.cartitem_set.all().delete()
    return cart
