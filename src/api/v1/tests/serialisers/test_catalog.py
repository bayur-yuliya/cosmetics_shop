import pytest

from api.v1.serializers.catalog import ProductWriteSerializer


@pytest.mark.django_db
def test_product_write_serializer_valid(tag, brand, group):
    data = {
        "name": "Test product",
        "group": group.id,
        "brand": brand.id,
        "price": "100.00",
        "description": "desc",
        "stock": 10,
        "tags": [tag.id],
        "is_active": True,
    }

    serializer = ProductWriteSerializer(data=data)
    assert serializer.is_valid(), serializer.errors


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
