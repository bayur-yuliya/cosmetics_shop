from django.contrib import messages
from django.db.models import QuerySet
from django.http import HttpRequest

from accounts.models import CustomUser
from cosmetics_shop.models import Cart, Product, CartItem, Client


def get_or_create_cart(request: HttpRequest) -> Cart:
    if request.user.is_authenticated:
        cart, _ = Cart.objects.get_or_create(user=request.user)
    else:
        cart_id = request.session.get("cart_id")
        if cart_id:
            try:
                cart = Cart.objects.get(pk=cart_id)
            except Cart.DoesNotExist:
                cart = Cart.objects.create()
                request.session["cart_id"] = cart.id
        else:
            cart = Cart.objects.create()
            request.session["cart_id"] = cart.id
    return cart


def get_cart_item(user: CustomUser, product_code: int) -> CartItem:
    product = Product.objects.get(code=product_code)
    cart, _ = Cart.objects.get_or_create(user=user)
    item, created = CartItem.objects.get_or_create(cart=cart, product=product)
    return item


def add_product_to_cart(cart: Cart, product_code: int) -> None:
    product = Product.objects.get(code=product_code)

    item, created = CartItem.objects.get_or_create(cart=cart, product=product)
    if item.quantity < item.product.stock:
        item.quantity += 1
    item.save()


def remove_product_from_cart(cart: Cart, product_code: int) -> None:
    product = Product.objects.get(code=product_code)

    try:
        item = CartItem.objects.get(cart=cart, product=product)
        if item.quantity > 1:
            item.quantity -= 1
            item.save()
    except CartItem.DoesNotExist:
        pass


def delete_product_from_cart(request: HttpRequest, product_id: int) -> None:
    cart = get_or_create_cart(request)
    product = Product.objects.get(pk=product_id)
    CartItem.objects.filter(cart=cart, product=product).delete()
    messages.success(request, "Товар успешно удален")


def delete_cart(request: HttpRequest) -> None:
    cart = get_or_create_cart(request)
    CartItem.objects.filter(cart=cart).delete()
    messages.success(request, "Корзина очищена")


def calculate_cart_total(cart: Cart) -> float:
    return sum(item.product.price * item.quantity for item in cart.cartitem_set.all())


def calculate_product_total_price(
    cart_items: QuerySet[CartItem], product_code: int
) -> float:
    product_count: CartItem | None = cart_items.filter(
        product__code=product_code
    ).first()
    if product_count is not None:
        return product_count.quantity * product_count.product.price
    return 0.0


def get_or_create_cart_for_session(request: HttpRequest) -> Cart:
    cart_id = request.session.get("cart_id")

    if cart_id:
        try:
            return Cart.objects.get(pk=cart_id)
        except Cart.DoesNotExist:
            del request.session["cart_id"]

    cart = Cart.objects.create()
    request.session["cart_id"] = cart.id
    return cart


def get_or_create_session_client(request: HttpRequest, form=None) -> Client | None:
    client_id = request.session.get("client_id")

    if client_id:
        try:
            return Client.objects.get(pk=client_id)
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


def clear_cart_after_order(request: HttpRequest) -> Cart:
    cart = get_or_create_cart(request)
    cart.cartitem_set.all().delete()
    return cart


def is_product_in_cart(request: HttpRequest, product_id: int) -> bool:
    cart = get_or_create_cart(request)
    cart_products = set(
        CartItem.objects.filter(cart=cart).values_list("product_id", flat=True)
    )
    return product_id in cart_products


def get_id_products_in_cart(request: HttpRequest) -> set[int]:
    cart = get_or_create_cart(request)
    cart_products = set(
        CartItem.objects.filter(cart=cart).values_list("product_id", flat=True)
    )
    return cart_products
