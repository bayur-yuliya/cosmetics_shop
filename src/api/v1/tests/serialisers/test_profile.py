import pytest


@pytest.mark.django_db
def test_favorite_duplicate(user, product):
    from api.v1.serializers.profile import FavoriteSerializer
    from cosmetics_shop.models import Favorite

    Favorite.objects.create(user=user, product=product)

    serializer = FavoriteSerializer(
        data={"product_id": product.id},
        context={"request": type("obj", (), {"user": user})()},
    )

    assert not serializer.is_valid()
    assert "non_field_errors" in serializer.errors
