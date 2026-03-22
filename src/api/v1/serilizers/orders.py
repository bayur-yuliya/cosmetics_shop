from rest_framework import serializers

from cosmetics_shop.models import Order, OrderItem


class ClientDataSerializer(serializers.Serializer):
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    email = serializers.EmailField()
    phone = serializers.CharField()


class AddressDataSerializer(serializers.Serializer):
    city = serializers.CharField()
    street = serializers.CharField()
    post_office = serializers.CharField()


class OrderCreateSerializer(serializers.Serializer):
    client_data = ClientDataSerializer(required=False)
    address_data = AddressDataSerializer(required=False)

    def validate(self, attrs):
        request = self.context["request"]

        if not request.user.is_authenticated:
            if not attrs.get("client_data") or not attrs.get("address_data"):
                raise serializers.ValidationError(
                    "Для неавторизованных пользователей"
                    "нужны client_data и address_data"
                )

        return attrs


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ["snapshot_product", "price", "quantity"]


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(source="order_items", many=True)

    class Meta:
        model = Order
        fields = [
            "id",
            "code",
            "status",
            "total_price",
            "created_at",
            "items",
        ]
