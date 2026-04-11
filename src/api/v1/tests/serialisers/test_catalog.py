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
