from typing import Any

from cosmetics_shop.models import Category


def context_categories() -> list[dict[str, Any]]:
    categories = Category.objects.all().prefetch_related("groupproduct_set")
    context_values: list[dict[str, Any]] = []
    for category in categories:
        groups = category.groupproduct_set.all()
        context_values.append({"category": category, "permissions": groups})
    return context_values
