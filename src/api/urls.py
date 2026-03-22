from rest_framework.routers import DefaultRouter

from api.v1.views.products import ProductViewSet

router = DefaultRouter()
router.register(r"products", ProductViewSet, basename="product")

urlpatterns = router.urls
