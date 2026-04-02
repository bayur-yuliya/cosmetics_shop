from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from api.v1.views.cart import CartViewSet
from api.v1.views.catalog import (
    BrandViewSet,
    CategoryViewSet,
    GroupProductViewSet,
    ProductViewSet,
)
from api.v1.views.orders import OrderViewSet
from cosmetics_shop.views.orders import mono_webhook

router = DefaultRouter()
# catalog
router.register(r"catalog/products", ProductViewSet, basename="products")
(router.register(r"catalog/brands", BrandViewSet, basename="brands"),)
(router.register(r"catalog/categories", CategoryViewSet, basename="categories"),)
(router.register(r"catalog/group", GroupProductViewSet, basename="groups"),)
# order
router.register(r"orders", OrderViewSet, basename="orders")
# cart
router.register(r"cart", CartViewSet, basename="cart")


# router.register(r"profile/orders", ProfileOrderViewSet, basename="profile-order")
# router.register(r"profile/favorites", ProfileFavoriteViewSet,
#                 basename="profile-favorite")


urlpatterns = [
    path("", include(router.urls)),
    # JWT
    path("token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    # path("orders/create/", CreateOrderAPIView.as_view()),
    path("payments/webhook/", mono_webhook),
]
