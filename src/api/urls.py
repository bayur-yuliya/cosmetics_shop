from django.urls import path
from rest_framework.routers import DefaultRouter

from api.v1.views import auth, cart, catalog, orders, profile
from cosmetics_shop.views.orders import mono_webhook

router = DefaultRouter()
# catalog
router.register(r"catalog/brands", catalog.BrandViewSet, basename="brands")
router.register(r"catalog/categories", catalog.CategoryViewSet, basename="categories")
router.register(r"catalog/group", catalog.GroupProductViewSet, basename="groups")
router.register(r"catalog/products", catalog.ProductViewSet, basename="products")
# order
router.register(r"orders", orders.OrderViewSet, basename="orders")
# cart
router.register(r"cart", cart.CartViewSet, basename="cart")
# profile
router.register(r"favorites", profile.FavoriteViewSet, basename="favorite")

urlpatterns = [
    path("login/", auth.LoginView.as_view()),
    path("register/", auth.RegisterView.as_view()),
    # payments
    path("payments/webhook/", mono_webhook),
    path("profile/orders/history/", profile.OrderHistoryListAPIView.as_view()),
] + router.urls
