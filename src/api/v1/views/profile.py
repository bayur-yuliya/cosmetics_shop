from rest_framework import generics, mixins, viewsets
from rest_framework.permissions import IsAuthenticated

from cosmetics_shop.models import Client, Favorite, Order

from ..serializers.orders import OrderSerializer
from ..serializers.profile import FavoriteSerializer


class FavoriteViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = FavoriteSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "product_id"

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return Favorite.objects.none()

        queryset = Favorite.objects.filter(user=self.request.user)
        if self.action == "list":
            return queryset.select_related("product")
        return queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class OrderHistoryListAPIView(generics.ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return Order.objects.none()
        client = Client.objects.filter(user=self.request.user).first()
        if not client:
            return Order.objects.none()

        # prefetch_related('order_items') is needed because the OrderSerializer
        # has a nested OrderItemSerializer
        return (
            Order.objects.filter(client=client)
            .prefetch_related("order_items")
            .order_by("-created_at")
        )
