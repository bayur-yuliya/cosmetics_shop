from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api.v1.serializers.orders import OrderSerializer
from cosmetics_shop.models import Order


class UserOrdersAPIView(ListAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        client = request.user.client

        orders = Order.objects.filter(client=client).prefetch_related("order_items")

        serializer = OrderSerializer(orders, many=True)

        return Response(serializer.data)
