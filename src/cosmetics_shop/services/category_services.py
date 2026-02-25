from typing import Any

from django.db.models import QuerySet

from cosmetics_shop.models import Category, Brand


def context_categories() -> list[dict[str, Any]]:
    categories = Category.objects.all().prefetch_related("groupproduct_set")
    context_values: list[dict[str, Any]] = []
    for category in categories:
        groups = category.groupproduct_set.all()
        context_values.append({"category": category, "groups": groups})
    return context_values


def get_grouped_for_alphabet_brands(brands: QuerySet[Brand]):
    grouped: dict[str, list[Brand]] = {}

    for brand in brands:
        letter = brand.name[0].upper()
        grouped.setdefault(letter, []).append(brand)

    return grouped
