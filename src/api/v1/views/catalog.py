from django.db.models import Exists, OuterRef
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from api.v1.filters import ProductFilter
from api.v1.permissions import ProductPermission
from api.v1.serializers.catalog import (
    BrandSerializer,
    CategorySerializer,
    GroupSerializer,
    ProductDetailSerializer,
    ProductListSerializer,
    ProductWriteSerializer,
)
from cosmetics_shop.models import Brand, Category, Favorite, GroupProduct, Product


class ProductViewSet(ModelViewSet):
    queryset = Product.objects.for_catalog()
    permission_classes = [ProductPermission]

    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = ProductFilter
    search_fields = ["name", "description"]
    ordering_fields = ["price", "created_at", "stock"]

    def get_serializer_class(self):
        if self.action == "list":
            return ProductListSerializer
        elif self.action == "retrieve":
            return ProductDetailSerializer
        return ProductWriteSerializer

    def get_queryset(self):
        qs = super().get_queryset()

        if self.request.user.is_authenticated:
            favorites_subquery = Favorite.objects.filter(
                user=self.request.user, product_id=OuterRef("pk")
            )
            qs = qs.annotate(is_favorite=Exists(favorites_subquery))

        if not self.request.user.is_staff:
            qs = qs.filter(is_active=True)

        return qs

    @action(methods=["post"], detail=True)
    def soft_delete(self, request, pk=None):
        product = self.get_object()
        product.soft_delete()
        return Response({"status": "product deactivated"})


class BrandViewSet(ReadOnlyModelViewSet):
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer
    lookup_field = "slug"


class CategoryViewSet(ReadOnlyModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    lookup_field = "slug"


class GroupProductViewSet(ReadOnlyModelViewSet):
    queryset = GroupProduct.objects.all()
    serializer_class = GroupSerializer
    lookup_field = "slug"
