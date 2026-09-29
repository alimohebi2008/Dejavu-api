from rest_framework.routers import DefaultRouter

from .views import (
    CategoryViewSet,
    ProductSizeViewSet,
    ProductViewSet,
    ProductColorViewSet,
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
    basename="product_size",
)

router.register(
    "products",
    ProductViewSet,
    basename="product",
)

router.register(
    "product_color",
    ProductColorViewSet,
    basename="product_color",
)

urlpatterns = router.urls
