from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import serializers
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from api.v1.serializers.cart import CartItemSerializer
from cosmetics_shop.models import CartItem
from cosmetics_shop.services.cart_services import (
    add_product_to_cart,
    delete_product_from_cart,
    get_cart_total_price,
    remove_product_from_cart,
)
from cosmetics_shop.utils.cart_utils import get_cart, get_or_create_cart


class CartViewSet(ViewSet):
    permission_classes = [AllowAny]

    def list(self, request):
        cart = get_cart(request)

        if not cart:
            return Response({"items": [], "total_price": 0})

        items = CartItem.objects.select_related("product").filter(cart=cart)
        serializer = CartItemSerializer(items, many=True)

        return Response(
            {"items": serializer.data, "total_price": get_cart_total_price(items)}
        )

    @extend_schema(
        summary="Add product in cart",
        request=inline_serializer(
            name="CartActionAddRequest",
            fields={"product_code": serializers.IntegerField()},
        ),
        responses={
            200: inline_serializer(
                name="CartSuccess", fields={"status": serializers.CharField()}
            )
        },
    )
    @action(detail=False, methods=["post"])
    def add(self, request):
        product_code = request.data.get("product_code")

        if not product_code:
            return Response({"error": "product_code required"}, status=400)

        cart = get_or_create_cart(request)
        add_product_to_cart(cart, int(product_code))

        return Response({"status": "added"})

    @extend_schema(
        summary="Remove product at cart",
        request=inline_serializer(
            name="CartActionRemoveRequest",
            fields={"product_code": serializers.IntegerField()},
        ),
        responses={
            200: inline_serializer(
                name="CartSuccess",
                fields={"status": serializers.CharField()},
            )
        },
    )
    @action(detail=False, methods=["post"])
    def remove(self, request):
        product_code = request.data.get("product_code")

        if not product_code:
            return Response({"error": "product_code required"}, status=400)

        cart = get_cart(request)
        if not cart:
            return Response({"error": "cart not found"}, status=404)

        remove_product_from_cart(cart, int(product_code))

        return Response({"status": "decreased"})

    @extend_schema(
        summary="Delete product at cart",
        request=inline_serializer(
            name="CartActionDeleteRequest",
            fields={"product_code": serializers.IntegerField()},
        ),
        responses={
            200: inline_serializer(
                name="DeleteCartSuccess", fields={"status": serializers.CharField()}
            )
        },
    )
    @action(detail=False, methods=["post"])
    def delete(self, request):
        product_code = request.data.get("product_code")

        if not product_code:
            return Response({"error": "product_code required"}, status=400)

        cart = get_cart(request)
        if not cart:
            return Response({"error": "cart not found"}, status=404)

        delete_product_from_cart(cart, int(product_code))

        return Response({"status": "deleted"})

    @extend_schema(
        summary="Clear cart",
        responses={
            200: inline_serializer(
                name="ClearCartSuccess", fields={"status": serializers.CharField()}
            )
        },
    )
    @action(detail=False, methods=["post"])
    def clear(self, request):
        cart = get_cart(request)

        if not cart:
            return Response({"status": "empty"})

        cart.cart_items.all().delete()

        return Response({"status": "cleared"})
