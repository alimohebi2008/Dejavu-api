from rest_framework.routers import DefaultRouter

from .views import (
    CartItemViewSet,
    CartViewSet,
    OrderItemViewSet,
    OrderViewSet,
    WishlistViewSet
)

router = DefaultRouter()

router.register("cart", CartViewSet, basename="cart")
router.register("cart-items", CartItemViewSet, basename="cart-item")
router.register("orders", OrderViewSet, basename="order")
router.register("order-items", OrderItemViewSet, basename="order-item")
router.register("wishlist", WishlistViewSet, basename="wishlist",
                )

urlpatterns = router.urls
