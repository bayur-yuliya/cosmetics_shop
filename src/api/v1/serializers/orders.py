from rest_framework import serializers

from cosmetics_shop.models import Order, OrderItem


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ["id", "snapshot_product", "quantity", "price"]


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(source="order_items", many=True)

    class Meta:
        model = Order
        fields = [
            "id",
            "snapshot_name",
            "snapshot_phone",
            "snapshot_email",
            "snapshot_address",
            "total_price",
            "status",
            "created_at",
            "items",
        ]


class ClientDataSerializer(serializers.Serializer):
    first_name = serializers.CharField(max_length=50, required=True)
    last_name = serializers.CharField(max_length=50, required=True)
    email = serializers.EmailField(required=True)
    phone = serializers.CharField(max_length=20, required=True)


class AddressDataSerializer(serializers.Serializer):
    city = serializers.CharField(max_length=100, required=True)
    post_office = serializers.CharField(max_length=100, required=True)


class OrderCreateSerializer(serializers.Serializer):
    payment_method = serializers.ChoiceField(choices=["card", "cash"], default="card")
    client_data = ClientDataSerializer(required=False)
    address_data = AddressDataSerializer(required=False)

    def validate(self, attrs):
        # Если API поддерживает анонимных пользователей (без профиля),
        # можно добавить проверку, что данные обязательно переданы.
        request = self.context.get("request")
        if request and not request.user.is_authenticated:
            if "client_data" not in attrs or "address_data" not in attrs:
                raise serializers.ValidationError(
                    "Для оформления заказа без регистрации необходимо передать "
                    "client_data и address_data."
                )
        return attrs
