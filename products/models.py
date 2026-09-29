from django.db import models


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
        verbose_name="کد رنگ",
    )
    class Meta:
        verbose_name = "رنگ محصول"
        verbose_name_plural = "رنگ های محصول"
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
    title = models.CharField(
        max_length=200,
        verbose_name="عنوان",
    )
    slug = models.SlugField(
        max_length=220,
        unique=True,
        verbose_name="اسلاگ",
    )
    description = models.TextField(
        verbose_name="توضیحات",
    )
    price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
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
    colors = models.ManyToManyField(
        ProductColor,
        related_name="products",
        blank=True,
        verbose_name="رنگ ها ",
    )

    class Meta:
        verbose_name = "محصول"
        verbose_name_plural = "محصولات"

    def __str__(self):
        return self.title


