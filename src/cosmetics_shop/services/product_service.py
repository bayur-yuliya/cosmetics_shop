import logging

from django.db.models import Exists, F, OuterRef, QuerySet

from accounts.models import CustomUser
from cosmetics_shop.models import Favorite, Product

logger = logging.getLogger(__name__)


def restore_stock_product(product_code: int, count: int) -> None:
    logger.debug(f"Restoring stock: product_code={product_code}, count={count}")
    Product.objects.filter(code=product_code).update(stock=F("stock") + count)


def change_stock_product(product_code: int, count: int) -> None:
    logger.debug(f"Stock update attempt: product_code={product_code}, count={count}")

    updated = Product.objects.filter(code=product_code, stock__gte=count).update(
        stock=F("stock") - count
    )
    if not updated:
        logger.warning(
            f"Out of stock: product_code={product_code}, " f"requested={count}"
        )
        raise ValueError("Товара недостаточно на складе")

    logger.info(f"Stock updated: product_code={product_code}, decreased_by={count}")


def favorites_products(user: CustomUser) -> QuerySet[Product]:
    logger.debug(f"Fetching favorite products for user_id={user.id}")

    favorites_subquery = Favorite.objects.filter(user=user, product_id=OuterRef("pk"))

    products = (
        (
            Product.objects.filter(is_active=True).annotate(
                is_favorite=Exists(favorites_subquery)
            )
        )
        .order_by("-stock")
        .for_catalog()
    )

    logger.debug("Favorite products queryset prepared")

    return products
