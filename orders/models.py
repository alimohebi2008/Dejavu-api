from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import F, Sum
from django.conf import settings
from products.models import Product


class Cart(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="cart",
        verbose_name="کاربر",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="تاریخ ایجاد",
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="تاریخ بروزرسانی",
    )

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "سبد خرید"
        verbose_name_plural = "سبدهای خرید"

    def __str__(self):
        return f"سبد خرید - {self.user.username}"


class CartItem(models.Model):
    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name="سبد خرید",
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="cart_items",
        verbose_name="محصول",
    )
    quantity = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1)],
        verbose_name="تعداد",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="تاریخ ایجاد",
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="تاریخ بروزرسانی",
    )

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "آیتم سبد خرید"
        verbose_name_plural = "آیتم‌های سبد خرید"
        constraints = [
            models.UniqueConstraint(
                fields=["cart", "product"],
                name="unique_product_in_cart",
            )
        ]

    def __str__(self):
        return f"{self.product.title} × {self.quantity}"


class Order(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "در انتظار پرداخت"
        PROCESSING = "processing", "در حال پردازش"
        SHIPPED = "shipped", "ارسال شده"
        DELIVERED = "delivered", "تحویل داده شده"
        CANCELLED = "cancelled", "لغو شده"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="orders",
        verbose_name="کاربر",
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        verbose_name="وضعیت سفارش",
    )
    total_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        verbose_name="مبلغ کل",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="تاریخ ایجاد",
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="تاریخ بروزرسانی",
    )

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "سفارش"
        verbose_name_plural = "سفارش‌ها"

    def __str__(self):
        return f"سفارش #{self.id} - {self.user.username}"

    def recalculate_total(self, save=True):
        total = self.items.aggregate(
            total=Sum(F("price") * F("quantity"))
        )["total"] or 0

        self.total_price = total

        if save:
            self.save(update_fields=["total_price", "updated_at"])

        return total


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name="سفارش",
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name="order_items",
        verbose_name="محصول",
    )
    quantity = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        verbose_name="تعداد",
    )
    price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name="قیمت",
    )

    class Meta:
        verbose_name = "آیتم سفارش"
        verbose_name_plural = "آیتم‌های سفارش"
        constraints = [
            models.UniqueConstraint(
                fields=["order", "product"],
                name="unique_product_in_order",
            )
        ]

    def __str__(self):
        return f"{self.product.title} × {self.quantity}"


class Wishlist(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="wishlist",
        verbose_name="کاربر",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="تاریخ ایجاد",
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="تاریخ بروزرسانی",
    )

    class Meta:
        verbose_name = "لیست علاقه‌مندی"
        verbose_name_plural = "لیست‌های علاقه‌مندی"

    def __str__(self):
        return f"Wishlist - {self.user.username}"


class WishlistItem(models.Model):
    wishlist = models.ForeignKey(
        Wishlist,
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name="لیست علاقه‌مندی",
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="wishlist_items",
        verbose_name="محصول",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="تاریخ افزودن",
    )

    class Meta:
        verbose_name = "آیتم علاقه‌مندی"
        verbose_name_plural = "آیتم‌های علاقه‌مندی"
        constraints = [
            models.UniqueConstraint(
                fields=["wishlist", "product"],
                name="unique_wishlist_product",
            ),
        ]
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.wishlist.user.username} - {self.product.title}"
