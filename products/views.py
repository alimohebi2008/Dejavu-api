from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets

from settings.permissions import IsAdminRoleOrReadOnly

from settings.filters import ProductFilter, CategoryFilter
from .models import Category, Product, ProductSize, ProductColor, ProductDiscount
from .serializers import (
    CategorySerializer,
    ProductSerializer,
    ProductSizeSerializer,
    ProductColorSerializer,
    ProductDiscountSerializer
)


class CategoryViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdminRoleOrReadOnly]
    queryset = Category.objects.all().order_by('-created_at')
    serializer_class = CategorySerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = CategoryFilter


class ProductSizeViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdminRoleOrReadOnly]
    queryset = ProductSize.objects.all()
    serializer_class = ProductSizeSerializer


class ProductViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdminRoleOrReadOnly]
    queryset = Product.objects.all().order_by('-created_at')
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = ProductFilter


class ProductColorViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdminRoleOrReadOnly]
    queryset = ProductColor.objects.all()
    serializer_class = ProductColorSerializer


class ProductDiscountViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdminRoleOrReadOnly]
    queryset = ProductDiscount.objects.all().order_by('-created_at')
    serializer_class = ProductDiscountSerializer
