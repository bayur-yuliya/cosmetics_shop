from django.db.models import OuterRef, Exists

from cosmetics_shop.models import Category, Favorite, Product


def context_categories():
    categories = Category.objects.all().prefetch_related("groupproduct_set")
    context_categories = []
    for category in categories:
        groups = category.groupproduct_set.all()
        context_categories.append({"category": category, "groups": groups})
    return context_categories


def favorites_products(request):
    favorites_subquery = Favorite.objects.filter(
        user=request.user,
        product_id=OuterRef('pk')
    )

    products = (
        Product.objects
        .annotate(is_favorite=Exists(favorites_subquery))
    ).order_by("-stock")

    return products
