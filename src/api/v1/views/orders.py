from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from api.v1.serilizers.orders import OrderCreateSerializer, OrderSerializer
from cosmetics_shop.models import Cart, Order
from cosmetics_shop.services.order_service import create_order_from_cart


class OrderViewSet(GenericViewSet, ListModelMixin, RetrieveModelMixin):
    serializer_class = OrderSerializer

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return self.request.user.client.orders.prefetch_related(
                "order_items"
            ).order_by("-created_at")
        return Order.objects.none()

    def get_serializer_class(self):
        if self.action == "create":
            return OrderCreateSerializer
        return OrderSerializer

    def create(self, request, *args, **kwargs):
        serializer = OrderCreateSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)

        cart = None
        if request.user.is_authenticated:
            cart = get_object_or_404(Cart, user=request.user)
        else:
            cart = get_object_or_404(Cart, session_key=request.session.session_key)

        try:
            order = create_order_from_cart(
                cart=cart,
                client_data=serializer.validated_data.get("client_data"),
                address_data=serializer.validated_data.get("address_data"),
            )
        except Exception as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            OrderSerializer(order).data,
            status=status.HTTP_201_CREATED,
        )
