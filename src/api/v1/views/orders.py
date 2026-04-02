import logging

from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from api.v1.permissions import IsAdminOrOwnerReadOnly
from api.v1.serializers.orders import OrderCreateSerializer, OrderSerializer
from cosmetics_shop.models import CartItem, Order, Payment, Status
from cosmetics_shop.services.order_service import create_order_from_cart
from cosmetics_shop.services.payment_service import init_payment
from cosmetics_shop.utils.cart_utils import get_cart
from utils.custom_exceptions import OutOfStockError

logger = logging.getLogger(__name__)


class OrderViewSet(ModelViewSet):
    queryset = Order.objects.all().prefetch_related("order_items")
    permission_classes = [AllowAny, IsAdminOrOwnerReadOnly]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return self.queryset
        return self.queryset.filter(client__user=user)

    def get_serializer_class(self):
        if self.action == "create":
            return OrderCreateSerializer
        return OrderSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"request": self.request})
        return context

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        cart = get_cart(request)
        if not cart:
            return Response(
                {"detail": "Корзина не найдена"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not CartItem.objects.filter(cart=cart).exists():
            return Response(
                {"detail": "Корзина пуста"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if cart.user and cart.user != request.user:
            return Response(
                {"detail": "У вас нет прав на эту корзину"},
                status=status.HTTP_403_FORBIDDEN,
            )

        try:
            order = create_order_from_cart(
                cart=cart,
                client_data=serializer.validated_data.get("client_data"),
                address_data=serializer.validated_data.get("address_data"),
            )
        except OutOfStockError as e:
            return Response({"detail": str(e)}, status=status.HTTP_409_CONFLICT)
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        payment_method = serializer.validated_data["payment_method"]
        response_data = {
            "order_id": order.id,
            "message": "Заказ успешно создан",
        }

        if payment_method == "card":
            try:
                payment_url = init_payment(order, request)
                response_data["payment_url"] = payment_url
            except Exception as e:
                logger.error(f"MonoBank Init Error for order {order.id}: {e}")

                order.set_status(
                    Status.PAYMENT_FAILED,
                    comment=f"Техническая ошибка при создании счета: {str(e)}",
                )

                Payment.objects.create(
                    order=order,
                    method=Payment.PaymentMethod.CARD,
                    amount=order.total_price,
                    status=Payment.PaymentStatus.FAILED,
                )
                response_data["message"] = (
                    "Заказ принят, но мы не смогли сформировать ссылку на оплату. "
                    "Наш менеджер свяжется с вами в ближайшее время."
                )
                response_data["order_status"] = "payment_failed"

        return Response(response_data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        if not request.user.is_staff:
            return Response(
                {"detail": "Действие запрещено"}, status=status.HTTP_403_FORBIDDEN
            )
        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        if not request.user.is_staff:
            return Response(
                {"detail": "Действие запрещено"}, status=status.HTTP_403_FORBIDDEN
            )
        return super().partial_update(request, *args, **kwargs)
