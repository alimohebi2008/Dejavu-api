from decimal import Decimal, ROUND_HALF_UP

from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, RegexValidator
from django.db import models
from django.db.models import F, Q
from django.utils import timezone


class ProductSize(models.Model):
    title = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="عنوان",
    )
    width = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        verbose_name="عرض",
    )
    length = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        verbose_name="طول",
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="فعال",
    )

    class Meta:
        verbose_name = "سایز محصول"
        verbose_name_plural = "سایزهای محصول"

    def __str__(self):
        return self.title


class Category(models.Model):
    title = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="عنوان",
    )
    slug = models.SlugField(
        max_length=120,
        unique=True,
        allow_unicode=True,
        verbose_name="اسلاگ",
    )
    description = models.TextField(
        blank=True,
        verbose_name="توضیحات",
    )
    image = models.ImageField(
        upload_to="categories/",
        blank=True,
        null=True,
        verbose_name="تصویر",
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="فعال",
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
        verbose_name = "دسته‌بندی"
        verbose_name_plural = "دسته‌بندی‌ها"

    def __str__(self):
        return self.title


class ProductColor(models.Model):
    title = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="عنوان",
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="فعال",
    )
    hex_code = models.CharField(
        max_length=7,
        validators=[
            RegexValidator(
                regex=r"^#(?:[0-9a-fA-F]{3}|[0-9a-fA-F]{6})$",
                message="کد رنگ باید به فرمت هگزادسیمال باشد، مثلاً #FF0000",
            ),
        ],
        verbose_name="کد رنگ",
    )

    class Meta:
        verbose_name = "رنگ محصول"
        verbose_name_plural = "رنگ‌های محصول"

    def __str__(self):
        return self.title


class Product(models.Model):
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name="products",
        verbose_name="دسته‌بندی",
    )
    sizes = models.ManyToManyField(
        ProductSize,
        related_name="products",
        blank=True,
        verbose_name="سایزها",
    )
    colors = models.ManyToManyField(
        ProductColor,
        related_name="products",
        blank=True,
        verbose_name="رنگ‌ها",
    )
    title = models.CharField(
        max_length=200,
        verbose_name="عنوان",
    )
    slug = models.SlugField(
        max_length=220,
        unique=True,
        allow_unicode=True,
        verbose_name="اسلاگ",
    )
    description = models.TextField(
        verbose_name="توضیحات",
    )
    price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name="قیمت",
    )
    stock = models.PositiveIntegerField(
        default=0,
        verbose_name="موجودی",
    )
    image = models.ImageField(
        upload_to="products/",
        blank=True,
        null=True,
        verbose_name="تصویر",
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="فعال",
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
        verbose_name = "محصول"
        verbose_name_plural = "محصولات"

    def __str__(self):
        return self.title

    @property
    def active_discount(self):

        discount = getattr(self, "discount", None)
        if discount and discount.is_currently_active():
            return discount
        return None

    @property
    def has_active_discount(self):
        return self.active_discount is not None

    @property
    def final_price(self):
        discount = self.active_discount
        if discount:
            return discount.apply_to(self.price)
        return self.price


class ProductDiscount(models.Model):
    class DiscountType(models.TextChoices):
        PERCENTAGE = "percentage", "درصدی"
        FIXED = "fixed", "مبلغ ثابت"

    product = models.OneToOneField(
        Product,
        on_delete=models.CASCADE,
        related_name="discount",
        verbose_name="محصول",
    )
    discount_type = models.CharField(
        max_length=20,
        choices=DiscountType.choices,
        verbose_name="نوع تخفیف",
    )
    value = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name="مقدار تخفیف",
        help_text="برای تخفیف درصدی عددی بین ۰ تا ۱۰۰، و برای مبلغ ثابت مبلغ تخفیف.",
    )
    start_at = models.DateTimeField(
        verbose_name="شروع تخفیف",
    )
    end_at = models.DateTimeField(
        verbose_name="پایان تخفیف",
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="فعال",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="تاریخ ایجاد",
    )

    class Meta:
        verbose_name = "تخفیف محصول"
        verbose_name_plural = "تخفیف‌های محصولات"
        constraints = [
            models.CheckConstraint(
                condition=Q(end_at__gt=F("start_at")),
                name="discount_end_after_start",
            ),
            models.CheckConstraint(
                condition=Q(discount_type="fixed") | Q(value__lte=100),
                name="discount_percentage_lte_100",
            ),
        ]

    def __str__(self):
        return f"{self.product.title} - {self.value}"

    def clean(self):
        errors = {}

        if self.start_at and self.end_at and self.end_at <= self.start_at:
            errors["end_at"] = "تاریخ پایان باید بعد از تاریخ شروع باشد."

        if self.value is not None:
            if (
                self.discount_type == self.DiscountType.PERCENTAGE
                and self.value > 100
            ):
                errors["value"] = "درصد تخفیف نمی‌تواند بیشتر از ۱۰۰ باشد."
            elif (
                self.discount_type == self.DiscountType.FIXED
                and self.product_id
                and self.value > self.product.price
            ):
                errors["value"] = "مبلغ تخفیف نمی‌تواند بیشتر از قیمت محصول باشد."

        if errors:
            raise ValidationError(errors)

    def is_currently_active(self):
        now = timezone.now()
        return self.is_active and self.start_at <= now <= self.end_at

    def apply_to(self, price):
        if self.discount_type == self.DiscountType.PERCENTAGE:
            discounted = price * (Decimal("100") - self.value) / Decimal("100")
        else:
            discounted = price - self.value
        discounted = max(discounted, Decimal("0"))
        return discounted.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)