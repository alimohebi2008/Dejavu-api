from rest_framework import serializers
from rest_framework import serializers

from products.models import Product
from .models import Wishlist, WishlistItem

from .models import Cart, CartItem, Order, OrderItem


class CartItemSerializer(serializers.ModelSerializer):
    product = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.filter(is_active=True),
    )
    product_title = serializers.CharField(
        source="product.title",
        read_only=True,
    )
    product_price = serializers.DecimalField(
        source="product.price",
        max_digits=12,
        decimal_places=2,
        read_only=True,
    )

    class Meta:
        model = CartItem
        fields = [
            "id",
            "product",
            "product_title",
            "product_price",
            "quantity",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "product_title",
            "product_price",
            "created_at",
            "updated_at",
        ]

    def validate(self, attrs):
        product = attrs.get(
            "product", self.instance.product if self.instance else None
        )
        quantity = attrs.get(
            "quantity", self.instance.quantity if self.instance else None
        )
        if (
            product is not None
            and quantity is not None
            and quantity > product.stock
        ):
            raise serializers.ValidationError(
                {"quantity": ["Requested quantity exceeds available stock."]}
            )
        if (
            self.instance is not None
            and product is not None
            and product.pk != self.instance.product_id
        ):
            request = self.context.get("request")
            if request is not None:
                duplicate = CartItem.objects.filter(
                    cart__user=request.user,
                    product=product,
                ).exclude(pk=self.instance.pk).exists()
                if duplicate:
                    raise serializers.ValidationError(
                        {"product": "This product is already in your cart."}
                    )

        return attrs


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)

    class Meta:
        model = Cart
        fields = [
            "id",
            "user",
            "items",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "user",
            "items",
            "created_at",
            "updated_at",
        ]


class OrderItemSerializer(serializers.ModelSerializer):
    product_title = serializers.CharField(
        source="product.title",
        read_only=True,
    )

    class Meta:
        model = OrderItem
        fields = [
            "id",
            "product",
            "product_title",
            "quantity",
            "price",
        ]
        read_only_fields = [
            "id",
            "product_title",
            "price",
        ]


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = [
            "id",
            "user",
            "status",
            "total_price",
            "items",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "user",
            "status",
            "total_price",
            "items",
            "created_at",
            "updated_at",
        ]


class WishlistItemSerializer(serializers.ModelSerializer):
    product = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.filter(is_active=True),
    )

    class Meta:
        model = WishlistItem
        fields = [
            "id",
            "product",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "created_at",
        ]


class WishlistSerializer(serializers.ModelSerializer):
    items = WishlistItemSerializer(
        many=True,
        read_only=True,
    )

    class Meta:
        model = Wishlist
        fields = [
            "id",
            "items",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
        ]
