from rest_framework import serializers

from .models import Category, Product,ProductSize,ProductColor,ProductDiscount


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = "__all__"


class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    class Meta:
        model = Product
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
