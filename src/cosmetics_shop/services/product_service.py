from django.db.models import QuerySet, Exists, OuterRef
from django.http import HttpRequest

from accounts.models import CustomUser
from cosmetics_shop.models import Product, Favorite


def favorites_products(user: CustomUser) -> QuerySet[Product]:
    favorites_subquery = Favorite.objects.filter(user=user, product_id=OuterRef("pk"))

    products = (
        Product.objects.filter(is_active=True).annotate(
            is_favorite=Exists(favorites_subquery)
        )
    ).order_by("-stock")

    return products


def get_ready_product_list(request: HttpRequest) -> QuerySet[Product]:
    if request.user.is_authenticated:
        products = favorites_products(request.user)
    else:
        products = Product.objects.filter(is_active=True)

    return products
