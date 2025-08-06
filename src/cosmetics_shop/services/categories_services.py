from cosmetics_shop.models import Category


def context_categories():
    categories = Category.objects.all().prefetch_related("groupproduct_set")
    context_categories = []
    for category in categories:
        groups = category.groupproduct_set.all()
        context_categories.append({"category": category, "groups": groups})
    return context_categories
