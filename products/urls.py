from rest_framework.routers import DefaultRouter

from .views import (
    CategoryViewSet,
    ProductSizeViewSet,
    ProductViewSet,
)


router = DefaultRouter()

router.register(
    "categories",
    CategoryViewSet,
    basename="category",
)

router.register(
    "sizes",
    ProductSizeViewSet,
    basename="product-size",
)

router.register(
    "products",
    ProductViewSet,
    basename="product",
)

urlpatterns = router.urls