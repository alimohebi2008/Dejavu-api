from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets

from accounts.models import RoleType
from settings.filters import CategoryFilter, ProductFilter
from settings.permissions import IsAdminRoleOrReadOnly

from .models import Category, Product, ProductColor, ProductDiscount, ProductSize
from .serializers import (
    CategorySerializer,
    ProductColorSerializer,
    ProductDiscountSerializer,
    ProductSerializer,
    ProductSizeSerializer,
)


def _is_admin_user(user):
    return bool(
        user.is_authenticated
        and user.role.filter(name=RoleType.ADMIN).exists()
    )


class CategoryViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdminRoleOrReadOnly]
    serializer_class = CategorySerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = CategoryFilter

    def get_queryset(self):
        queryset = Category.objects.all().order_by("-created_at")
        if not _is_admin_user(self.request.user):
            queryset = queryset.filter(is_active=True)
        return queryset


class ProductSizeViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdminRoleOrReadOnly]
    serializer_class = ProductSizeSerializer

    def get_queryset(self):
        queryset = ProductSize.objects.all()
        if not _is_admin_user(self.request.user):
            queryset = queryset.filter(is_active=True)
        return queryset


class ProductViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdminRoleOrReadOnly]
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = ProductFilter

    def get_queryset(self):
        queryset = Product.objects.select_related("category").prefetch_related(
            "sizes", "colors"
        ).order_by("-created_at")
        if not _is_admin_user(self.request.user):
            queryset = queryset.filter(is_active=True, category__is_active=True)
        return queryset


class ProductColorViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdminRoleOrReadOnly]
    serializer_class = ProductColorSerializer

    def get_queryset(self):
        queryset = ProductColor.objects.all()
        if not _is_admin_user(self.request.user):
            queryset = queryset.filter(is_active=True)
        return queryset


class ProductDiscountViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdminRoleOrReadOnly]
    serializer_class = ProductDiscountSerializer

    def get_queryset(self):
        queryset = ProductDiscount.objects.select_related(
            "product", "product__category"
        ).order_by("-created_at")
        if not _is_admin_user(self.request.user):
            now = timezone.now()
            queryset = queryset.filter(
                is_active=True,
                start_at__lte=now,
                end_at__gte=now,
                product__is_active=True,
                product__category__is_active=True,
            )
        return queryset
