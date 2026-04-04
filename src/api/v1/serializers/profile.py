from rest_framework import serializers

from api.v1.serializers.catalog import ProductShortListSerializer
from cosmetics_shop.models import Favorite, Product


class FavoriteSerializer(serializers.ModelSerializer):
    product = ProductShortListSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.filter(is_active=True),
        source="product",
        write_only=True,
    )

    class Meta:
        model = Favorite
        fields = ["id", "product", "product_id"]

    def validate(self, attrs):
        user = self.context["request"].user
        product = attrs["product"]
        if Favorite.objects.filter(user=user, product=product).exists():
            raise serializers.ValidationError("Этот товар уже в избранном.")
        return attrs
