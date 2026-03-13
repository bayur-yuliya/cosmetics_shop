from django.db.models import QuerySet
from django.http import HttpRequest

from cosmetics_shop.models import Product
from cosmetics_shop.services.product_service import favorites_products


def get_ready_product_list(request: HttpRequest) -> QuerySet[Product]:
    if request.user.is_authenticated:
        products = favorites_products(request.user)
    else:
        products = Product.objects.filter(is_active=True).for_catalog()

    return products
