from rest_framework.routers import DefaultRouter

from .views import (
    CategoryViewSet,
    ProductSizeViewSet,
    ProductViewSet,
    ProductColorViewSet,
    ProductDiscountViewSet,
)

router = DefaultRouter()

router.register(
    "categories",
    CategoryViewSet,
    basename="categories",
)

router.register(
    "sizes",
    ProductSizeViewSet,
    basename="product_size",
)

router.register(
    "products",
    ProductViewSet,
    basename="products",
)

router.register(
    "product_colors",
    ProductColorViewSet,
    basename="product_colors",
)
router.register(
    "product_discounts",
    ProductDiscountViewSet,
    basename="product_discounts",
)



urlpatterns = router.urls
