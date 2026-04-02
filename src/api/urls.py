from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from api.v1.views.catalog import (
    BrandViewSet,
    CategoryViewSet,
    GroupProductViewSet,
    ProductViewSet,
)
from api.v1.views.orders import OrderViewSet

router = DefaultRouter()
# catalog
router.register(r"catalog/products", ProductViewSet, basename="product")
(router.register(r"catalog/brands", BrandViewSet, basename="brand"),)
(router.register(r"catalog/categories", CategoryViewSet, basename="category"),)
(router.register(r"catalog/group", GroupProductViewSet, basename="group"),)
# order
router.register(r"orders", OrderViewSet, basename="order")

urlpatterns = [
    path("", include(router.urls)),
    # JWT
    path("token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
]
