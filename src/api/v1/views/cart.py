from rest_framework.decorators import action
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
    def list(self, request):
        cart = get_cart(request)

        if not cart:
            return Response({"items": [], "total_price": 0})

        items = CartItem.objects.select_related("product").filter(cart=cart)
        serializer = CartItemSerializer(items, many=True)

        return Response(
            {"items": serializer.data, "total_price": get_cart_total_price(items)}
        )

    @action(detail=False, methods=["post"])
    def add(self, request):
        product_code = request.data.get("product_code")

        if not product_code:
            return Response({"error": "product_code required"}, status=400)

        cart = get_or_create_cart(request)
        add_product_to_cart(cart, int(product_code))

        return Response({"status": "added"})

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

    @action(detail=False, methods=["post"])
    def delete(self, request):
        product_id = request.data.get("product_id")

        if not product_id:
            return Response({"error": "product_id required"}, status=400)

        cart = get_cart(request)
        if not cart:
            return Response({"error": "cart not found"}, status=404)

        delete_product_from_cart(cart, int(product_id))

        return Response({"status": "deleted"})

    @action(detail=False, methods=["post"])
    def clear(self, request):
        cart = get_cart(request)

        if not cart:
            return Response({"status": "empty"})

        cart.cart_items.all().delete()

        return Response({"status": "cleared"})
