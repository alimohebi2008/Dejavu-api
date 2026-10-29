from django.shortcuts import render
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.viewsets import ModelViewSet
from settings.permissions import IsAdminRole
from rest_framework import viewsets

from settings.filters import UserFilter
from .models import User, Role
from .serializers import UserSerializer, RoleSerializer
from products.models import Product,Category
from django.db.models import Sum
from rest_framework.response import Response
from settings.mixins import ProtectedDeleteErrorMixin


class RoleViewSet(ModelViewSet):
    permission_classes = [IsAdminRole]
    queryset = Role.objects.all()
    serializer_class = RoleSerializer


class UserViewSet(ProtectedDeleteErrorMixin, ModelViewSet):
    permission_classes = [IsAdminRole]
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = UserFilter


class DashboardView(viewsets.GenericViewSet):
    permission_classes = [IsAdminRole]

    def list(self, request, *args, **kwargs):
        total_products = Product.objects.count()

        total_stock = Product.objects.aggregate(
            total=Sum("stock")
        )["total"] or 0

        total_categories = Category.objects.count()

        discounted_products = Product.objects.filter(
            discount__gt=0
        ).count()

        latest_products = Product.objects.order_by(
            "-created_at"
        )[:4]

        latest_products_data = [
            {
                "id": product.id,
                "title": product.title,
            }
            for product in latest_products
        ]

        return Response({
            "total_products": total_products,
            "total_stock": total_stock,
            "total_categories": total_categories,
            "discounted_products": discounted_products,
            "latest_products": latest_products_data,
        })
