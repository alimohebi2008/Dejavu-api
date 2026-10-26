from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers

from .models import (
    Category,
    Product,
    ProductColor,
    ProductDiscount,
    ProductSize,
)


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = "__all__"


class ProductSizeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductSize
        fields = "__all__"


class ProductColorSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductColor
        fields = "__all__"


class ProductDiscountSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductDiscount
        fields = "__all__"

    def validate(self, attrs):
        instance = self.instance or ProductDiscount()
        for field, value in attrs.items():
            setattr(instance, field, value)

        try:
            instance.clean()
        except DjangoValidationError as exc:
            detail = exc.message_dict if hasattr(exc, "message_dict") else exc.messages
            raise serializers.ValidationError(detail) from exc

        return attrs


class NestedPrimaryKeyRelatedField(serializers.PrimaryKeyRelatedField):
    def __init__(self, *args, serializer_class=None, **kwargs):
        self.serializer_class = serializer_class
        super().__init__(*args, **kwargs)

    def use_pk_only_optimization(self):
        return False

    def to_representation(self, value):
        return self.serializer_class(value).data


class ProductSerializer(serializers.ModelSerializer):
    category = NestedPrimaryKeyRelatedField(
        queryset=Category.objects.all(), serializer_class=CategorySerializer
    )
    sizes = NestedPrimaryKeyRelatedField(
        queryset=ProductSize.objects.all(),
        serializer_class=ProductSizeSerializer,
        many=True,
        required=False,
    )
    colors = NestedPrimaryKeyRelatedField(
        queryset=ProductColor.objects.all(),
        serializer_class=ProductColorSerializer,
        many=True,
        required=False,
    )

    class Meta:
        model = Product
        fields = "__all__"