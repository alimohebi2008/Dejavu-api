from django.contrib import admin

from .models import Cart, CartItem, Order, OrderItem, Wishlist, WishlistItem


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    fields = (
        "product",
        "quantity",
        "created_at",
        "updated_at",
    )
    readonly_fields = (
        "created_at",
        "updated_at",
    )
    verbose_name = "آیتم سبد خرید"
    verbose_name_plural = "آیتم‌های سبد خرید"


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "created_at",
        "updated_at",
    )
    search_fields = (
        "user__username",
        "user__phone_number",
    )
    list_filter = (
        "created_at",
        "updated_at",
    )
    readonly_fields = (
        "created_at",
        "updated_at",
    )
    inlines = (CartItemInline,)

    @admin.display(description="شناسه")
    def id(self, obj):
        return obj.pk


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    fields = (
        "product",
        "quantity",
        "price",
    )
    verbose_name = "آیتم سفارش"
    verbose_name_plural = "آیتم‌های سفارش"


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "status",
        "total_price",
        "created_at",
        "updated_at",
    )
    search_fields = (
        "user__username",
        "user__phone_number",
    )
    list_filter = (
        "status",
        "created_at",
        "updated_at",
    )
    readonly_fields = (
        "total_price",
        "created_at",
        "updated_at",
    )
    inlines = (OrderItemInline,)

    @admin.display(description="شناسه")
    def id(self, obj):
        return obj.pk


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "cart",
        "product",
        "quantity",
        "created_at",
        "updated_at",
    )
    search_fields = (
        "cart__user__username",
        "product__title",
    )
    list_filter = (
        "created_at",
        "updated_at",
    )
    readonly_fields = (
        "created_at",
        "updated_at",
    )

    @admin.display(description="شناسه")
    def id(self, obj):
        return obj.pk


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "order",
        "product",
        "quantity",
        "price",
    )
    search_fields = (
        "order__user__username",
        "product__title",
    )

    @admin.display(description="شناسه")
    def id(self, obj):
        return obj.pk


class WishlistItemInline(admin.TabularInline):
    model = WishlistItem
    extra = 0
    fields = ("product", "created_at")
    readonly_fields = ("created_at",)


@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "created_at", "updated_at")
    search_fields = ("user__username", "user__phone_number")
    list_filter = ("created_at", "updated_at")
    readonly_fields = ("created_at", "updated_at")
    inlines = (WishlistItemInline,)

    @admin.display(description="شناسه")
    def id(self, obj):
        return obj.pk


@admin.register(WishlistItem)
class WishlistItemAdmin(admin.ModelAdmin):
    list_display = ("id", "wishlist", "product", "created_at")
    search_fields = ("wishlist__user__username", "product__title")
    list_filter = ("created_at",)
    readonly_fields = ("created_at",)

    @admin.display(description="شناسه")
    def id(self, obj):
        return obj.pk
