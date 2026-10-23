from rest_framework import status, viewsets
from rest_framework.decorators import action
from settings.permissions import HasAnyRole
from rest_framework.response import Response
from django.db import transaction
from django.shortcuts import get_object_or_404
from products.models import Product

from .models import Cart, CartItem, Order, OrderItem,Wishlist, WishlistItem
from .serializers import (
    CartItemSerializer,
    CartSerializer,
    OrderItemSerializer,
    OrderSerializer,
    WishlistSerializer,
    WishlistItemSerializer
)


class CartViewSet(viewsets.ModelViewSet):
    serializer_class = CartSerializer
    permission_classes = [HasAnyRole]
    http_method_names = ["get"]

    def get_queryset(self):
        return Cart.objects.filter(
            user=self.request.user
        )

    def get_object(self):
        cart, _ = Cart.objects.get_or_create(
            user=self.request.user
        )
        return cart


class CartItemViewSet(viewsets.ModelViewSet):
    serializer_class = CartItemSerializer
    permission_classes = [HasAnyRole]

    def get_queryset(self):
        return (
            CartItem.objects.filter(cart__user=self.request.user)
            .select_related("product", "cart")
        )

    @transaction.atomic
    def perform_create(self, serializer):
        cart, _ = Cart.objects.get_or_create(user=self.request.user)

        product = serializer.validated_data["product"]
        quantity = serializer.validated_data["quantity"]

        item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={"quantity": quantity},
        )

        if not created:
            item.quantity += quantity
            item.save(update_fields=["quantity", "updated_at"])
        serializer.instance = item


class OrderViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [HasAnyRole]

    def get_queryset(self):
        return (
            Order.objects.filter(user=self.request.user)
            .prefetch_related("items__product")
        )


class OrderItemViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = OrderItemSerializer
    permission_classes = [HasAnyRole]

    def get_queryset(self):
        return (
            OrderItem.objects.filter(order__user=self.request.user)
            .select_related("product", "order")
        )


class WishlistViewSet(viewsets.ModelViewSet):
    serializer_class = WishlistSerializer
    permission_classes = [HasAnyRole]
    http_method_names = ["get", "post", "delete"]

    def get_queryset(self):
        return Wishlist.objects.filter(
            user=self.request.user
        ).prefetch_related(
            "items__product"
        )

    def get_object(self):
        wishlist, _ = Wishlist.objects.get_or_create(
            user=self.request.user
        )
        return wishlist

    @action(
        detail=False,
        methods=["post"],
        url_path="add",
    )
    def add(self, request):
        product_id = request.data.get("product")

        if not product_id:
            return Response(
                {"detail": "شناسه محصول الزامی است."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        product = get_object_or_404(
            Product,
            id=product_id,
            is_active=True,
        )

        wishlist = self.get_object()

        item, created = WishlistItem.objects.get_or_create(
            wishlist=wishlist,
            product=product,
        )

        if not created:
            return Response(
                {"detail": "این محصول قبلاً در لیست علاقه‌مندی شما وجود دارد."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            {"detail": "محصول با موفقیت به علاقه‌مندی‌ها اضافه شد."},
            status=status.HTTP_201_CREATED,
        )

    @action(
        detail=False,
        methods=["delete"],
        url_path=r"remove/(?P<product_id>\d+)",
    )
    def remove(self, request, product_id):
        wishlist = self.get_object()

        item = get_object_or_404(
            WishlistItem,
            wishlist=wishlist,
            product_id=product_id,
        )

        item.delete()

        return Response(
            status=status.HTTP_204_NO_CONTENT
        )

class WishlistViewSet(viewsets.ModelViewSet):
    serializer_class = WishlistSerializer
    permission_classes = [HasAnyRole]
    http_method_names = ["get", "post", "delete"]

    def get_queryset(self):
        return Wishlist.objects.filter(
            user=self.request.user
        ).prefetch_related(
            "items__product"
        )

    def get_object(self):
        wishlist, _ = Wishlist.objects.get_or_create(
            user=self.request.user
        )
        return wishlist

    def list(self, request, *args, **kwargs):
        wishlist = self.get_object()
        serializer = self.get_serializer(wishlist)

        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        return self.add(request)

    @action(
        detail=False,
        methods=["post"],
        url_path="add",
    )
    def add(self, request):
        product_id = request.data.get("product")

        if not product_id:
            return Response(
                {"detail": "شناسه محصول الزامی است."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        product = get_object_or_404(
            Product,
            id=product_id,
            is_active=True,
        )

        wishlist = self.get_object()

        item, created = WishlistItem.objects.get_or_create(
            wishlist=wishlist,
            product=product,
        )

        if not created:
            return Response(
                {
                    "detail": "این محصول قبلاً در لیست علاقه‌مندی شما وجود دارد."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            {
                "detail": "محصول با موفقیت به لیست علاقه‌مندی‌ها اضافه شد."
            },
            status=status.HTTP_201_CREATED,
        )

    @action(
        detail=False,
        methods=["delete"],
        url_path=r"remove/(?P<product_id>\d+)",
    )
    def remove(self, request, product_id):
        wishlist = self.get_object()

        item = get_object_or_404(
            WishlistItem,
            wishlist=wishlist,
            product_id=product_id,
        )

        item.delete()

        return Response(
            status=status.HTTP_204_NO_CONTENT
        )