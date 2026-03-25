import logging
from typing import Any

from django.core.cache import cache
from django.db.models import QuerySet

from cosmetics_shop.models import Brand, Category

logger = logging.getLogger(__name__)


def context_categories() -> list[dict[str, Any]]:
    cache_key = "categories_with_groups"

    data = cache.get(cache_key)
    if data:
        logger.debug("Categories fetched from cache")
        return data

    categories = Category.objects.all().prefetch_related("groupproduct_set")

    context_values: list[dict[str, Any]] = [
        {"category": category, "groups": category.groupproduct_set.all()}
        for category in categories
    ]

    cache.set(cache_key, context_values, timeout=60 * 60)  # 1 hour

    logger.debug("Categories cached")

    return context_values


def get_grouped_for_alphabet_brands(brands: QuerySet[Brand]):
    grouped: dict[str, list[Brand]] = {}

    for brand in brands:
        letter = brand.name[0].upper()
        grouped.setdefault(letter, []).append(brand)

    return grouped
