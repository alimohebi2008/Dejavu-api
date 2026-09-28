from django.contrib import admin

from .models import Category, Product, ProductSize


@admin.register(ProductSize)
class ProductSizeAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "width",
        "length",
        "is_active",
    )
    search_fields = ("title",)
    list_filter = ("is_active",)

    @admin.display(description="شناسه")
    def id(self, obj):
        return obj.pk


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "slug",
        "is_active",
        "created_at",
        "updated_at",
    )
    search_fields = ("title", "slug")
    list_filter = ("is_active", "created_at")
    readonly_fields = ("created_at", "updated_at")
    prepopulated_fields = {"slug": ("title",)}


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "category",
        "price",
        "stock",
        "is_active",
        "created_at",
    )
    search_fields = (
        "title",
        "slug",
        "category__title",
    )
    list_filter = (
        "category",
        "is_active",
        "created_at",
    )
    readonly_fields = ("created_at", "updated_at")
    filter_horizontal = ("sizes",)
    prepopulated_fields = {"slug": ("title",)}