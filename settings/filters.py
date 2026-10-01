import django_filters
from django.db.models import Q

from products.models import Product, Category
from accounts.models import User


class ProductFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(method="filter_search")

    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(title__icontains=value) |
            Q(category__title__icontains=value)
        ).distinct()

    class Meta:
        model = Product
        fields = ["search"]



class CategoryFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(
        field_name="title",
        lookup_expr="icontains",
    )

    class Meta:
        model = Category
        fields = ["search"]


class UserFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(method="filter_search")

    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(first_name__icontains=value)
            | Q(last_name__icontains=value)
            | Q(username__icontains=value)
            | Q(phone_number__icontains=value)
        ).distinct()

    class Meta:
        model = User
        fields = ["search"]