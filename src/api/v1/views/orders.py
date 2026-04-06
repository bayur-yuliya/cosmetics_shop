import logging

from django.urls import reverse
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from api.v1.permissions import IsAdminOrOwnerReadOnly
from api.v1.serializers.orders import OrderCreateSerializer, OrderSerializer
from cosmetics_shop.models import Order, Payment, Status
from cosmetics_shop.payments.mono import init_payment
from cosmetics_shop.services.cart_services import clear_cart_after_order
from cosmetics_shop.services.order_service import create_order_from_cart
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
        return self.queryset.filter(client__user=user.id)

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

        if not cart.cart_items.exists():
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
            "status": order.get_status_display(),
            "payment_method": payment_method,
            "total_price": order.total_price,
            "message": "Заказ успешно создан",
        }

        if payment_method == "card":
            response_data.update(self._handle_card_payment(order, request))
        else:
            clear_cart_after_order(cart)
            response_data["message"] = "Заказ принят (оплата при получении)"

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

    def _handle_card_payment(self, order, request):
        fallback_url = reverse("orders-detail", kwargs={"pk": order.id})

        redirect_url = request.headers.get(
            "X-Frontend-Redirect-Url",
            fallback_url,
        )

        try:
            payment_url = init_payment(
                order,
                request,
                custom_redirect_url=redirect_url,
            )

            return {"payment_url": payment_url}

        except Exception as e:
            logger.error(f"MonoBank Init Error for order {order.id}: {e}")

            order.set_status(
                Status.PAYMENT_FAILED,
                comment=f"Ошибка оплаты: {str(e)}",
            )

            Payment.objects.create(
                order=order,
                method=Payment.PaymentMethod.CARD,
                amount=order.total_price,
                status=Payment.PaymentStatus.FAILED,
            )

            return {
                "payment_url": None,
                "payment_status": "failed",
                "message": "Ошибка создания ссылки на оплату",
            }
