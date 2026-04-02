from rest_framework import serializers

from cosmetics_shop.models import CartItem


class CartItemSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source="product.name", read_only=True)
    code = serializers.CharField(source="product.code", read_only=True)
    price = serializers.DecimalField(
        source="product.price", max_digits=10, decimal_places=2, read_only=True
    )

    class Meta:
        model = CartItem
        fields = [
            "id",
            "name",
            "code",
            "price",
            "quantity",
        ]
