from rest_framework.routers import DefaultRouter

from api.v1.views.orders import OrderViewSet
from api.v1.views.products import ProductViewSet

router = DefaultRouter()
router.register(r"products", ProductViewSet, basename="product")
router.register(r"orders", OrderViewSet, basename="orders")

urlpatterns = router.urls
