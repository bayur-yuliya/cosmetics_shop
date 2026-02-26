from django.db.models import QuerySet, Exists, OuterRef, F
from django.http import HttpRequest

from accounts.models import CustomUser
from cosmetics_shop.models import Product, Favorite


def change_stock_product(product_code: int, count: int) -> None:
    updated = Product.objects.filter(code=product_code, stock__gte=count).update(
        stock=F("stock") - count
    )
    if not updated:
        raise ValueError("Товара недостаточно на складе")


def favorites_products(user: CustomUser) -> QuerySet[Product]:
    favorites_subquery = Favorite.objects.filter(user=user, product_id=OuterRef("pk"))

    products = (
        Product.objects.filter(is_active=True).annotate(
            is_favorite=Exists(favorites_subquery)
        )
    ).order_by("-stock").for_catalog()

    return products


def get_ready_product_list(request: HttpRequest) -> QuerySet[Product]:
    if request.user.is_authenticated:
        products = favorites_products(request.user)
    else:
        products = Product.objects.filter(is_active=True).for_catalog()

    return products
