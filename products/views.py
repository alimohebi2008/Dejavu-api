from rest_framework import viewsets

from .models import Category, Product, ProductSize, ProductColor, ProductDiscount
from .serializers import (
    CategorySerializer,
    ProductSerializer,
    ProductSizeSerializer,
    ProductColorSerializer,
    ProductDiscountSerializer
)


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all().order_by('-created_at')
    serializer_class = CategorySerializer


class ProductSizeViewSet(viewsets.ModelViewSet):
    queryset = ProductSize.objects.all()
    serializer_class = ProductSizeSerializer


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all().order_by('-created_at')
    serializer_class = ProductSerializer


class ProductColorViewSet(viewsets.ModelViewSet):
    queryset = ProductColor.objects.all()
    serializer_class = ProductColorSerializer


class ProductDiscountViewSet(viewsets.ModelViewSet):
    queryset = ProductDiscount.objects.all().order_by('-created_at')
    serializer_class = ProductDiscountSerializer
