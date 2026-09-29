import random
import uuid
from datetime import timedelta
from decimal import Decimal

import factory
from django.utils import timezone
from factory import Faker
from factory.django import DjangoModelFactory
from faker import Faker as FakerLib

from .models import (
    Category,
    Product,
    ProductColor,
    ProductDiscount,
    ProductSize,
)

# python manage.py generate_to_db products.CategoryFactory -q 8
# python manage.py generate_to_db products.ProductSizeFactory -q 6
# python manage.py generate_to_db products.ProductColorFactory -q 10
# python manage.py generate_to_db products.ProductFactory -q 40
# python manage.py generate_to_db products.ProductDiscountFactory -q 15

fake = FakerLib('fa_IR')


SIZES = [
    (100, 150),
    (120, 180),
    (150, 200),
    (200, 300),
    (250, 350),
    (300, 400),
]


COLORS = [
    ('قرمز', '#E53935'),
    ('آبی', '#1E88E5'),
    ('سبز', '#43A047'),
    ('زرد', '#FDD835'),
    ('مشکی', '#212121'),
    ('سفید', '#FFFFFF'),
    ('طوسی', '#9E9E9E'),
    ('قهوه‌ای', '#6D4C41'),
    ('کرمی', '#F5F5DC'),
    ('سرمه‌ای', '#1A237E'),
]


class ProductSizeFactory(DjangoModelFactory):
    class Meta:
        model = ProductSize
        django_get_or_create = ('title',)

    class Params:
        dims = factory.Iterator(SIZES)

    title = factory.LazyAttribute(lambda o: f'{o.dims[0]}x{o.dims[1]}')
    width = factory.LazyAttribute(lambda o: Decimal(o.dims[0]))
    length = factory.LazyAttribute(lambda o: Decimal(o.dims[1]))
    is_active = True


class ProductColorFactory(DjangoModelFactory):
    class Meta:
        model = ProductColor
        django_get_or_create = ('title',)

    class Params:
        color = factory.Iterator(COLORS)

    title = factory.LazyAttribute(lambda o: o.color[0])
    hex_code = factory.LazyAttribute(lambda o: o.color[1])
    is_active = True


class CategoryFactory(DjangoModelFactory):
    class Meta:
        model = Category
        django_get_or_create = ('slug',)

    title = factory.Sequence(lambda n: f'دسته‌بندی {n + 1}')
    slug = factory.Sequence(lambda n: f'category-{n + 1}')
    description = Faker('paragraph', nb_sentences=2, locale='fa_IR')
    is_active = factory.LazyFunction(lambda: random.random() < 0.9)
    # image = factory.django.ImageField(color=factory.Faker('color'))


def random_category():
    if Category.objects.count() < 5:
        CategoryFactory.create_batch(5)
    return random.choice(list(Category.objects.all()))


class ProductFactory(DjangoModelFactory):
    class Meta:
        model = Product

    category = factory.LazyFunction(random_category)
    title = factory.LazyFunction(lambda: fake.sentence(nb_words=3).rstrip('.'))
    slug = factory.LazyFunction(lambda: f'product-{uuid.uuid4().hex[:10]}')
    description = Faker('paragraph', nb_sentences=4, locale='fa_IR')
    price = factory.LazyFunction(
        lambda: Decimal(random.randrange(100_000, 20_000_000, 10_000))
    )
    stock = Faker('random_int', min=0, max=200)
    is_active = factory.LazyFunction(lambda: random.random() < 0.9)
    # image = factory.django.ImageField(color=factory.Faker('color'))

    @factory.post_generation
    def sizes(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            self.sizes.add(*extracted)
        else:
            if ProductSize.objects.count() < len(SIZES):
                ProductSizeFactory.create_batch(len(SIZES))

            all_sizes = list(ProductSize.objects.all())
            selected = random.sample(all_sizes, random.randint(1, min(3, len(all_sizes))))
            self.sizes.add(*selected)

    @factory.post_generation
    def colors(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            self.colors.add(*extracted)
        else:
            if ProductColor.objects.count() < len(COLORS):
                ProductColorFactory.create_batch(len(COLORS))

            all_colors = list(ProductColor.objects.all())
            selected = random.sample(all_colors, random.randint(1, min(3, len(all_colors))))
            self.colors.add(*selected)


# ---------- discount ----------

def random_product_without_discount():
    # ProductDiscount با Product رابطه‌ی OneToOne داره
    product = Product.objects.filter(discount__isnull=True).order_by('?').first()
    return product or ProductFactory()


def discount_window(state):
    now = timezone.now()
    if state == 'expired':
        end = now - timedelta(days=random.randint(1, 10))
        start = end - timedelta(days=random.randint(5, 20))
    elif state == 'upcoming':
        start = now + timedelta(days=random.randint(1, 10))
        end = start + timedelta(days=random.randint(5, 20))
    else:  # active
        start = now - timedelta(days=random.randint(1, 10))
        end = now + timedelta(days=random.randint(1, 20))
    return start, end


def discount_value(discount_type, price):
    if discount_type == ProductDiscount.DiscountType.PERCENTAGE:
        return Decimal(random.choice([5, 10, 15, 20, 25, 30, 40, 50]))

    # مبلغ ثابت: بین ۵٪ تا ۵۰٪ قیمت، گرد‌شده به هزار (هیچ‌وقت بیشتر از قیمت نمی‌شه)
    amount = int(price * Decimal(random.uniform(0.05, 0.5)))
    return Decimal(max(amount // 1000 * 1000, 1000))


class ProductDiscountFactory(DjangoModelFactory):
    class Meta:
        model = ProductDiscount

    class Params:
        state = factory.LazyFunction(
            lambda: random.choices(['active', 'expired', 'upcoming'], weights=[70, 15, 15])[0]
        )
        window = factory.LazyAttribute(lambda o: discount_window(o.state))

    product = factory.LazyFunction(random_product_without_discount)
    discount_type = factory.LazyFunction(
        lambda: random.choice(ProductDiscount.DiscountType.values)
    )
    value = factory.LazyAttribute(lambda o: discount_value(o.discount_type, o.product.price))
    start_at = factory.LazyAttribute(lambda o: o.window[0])
    end_at = factory.LazyAttribute(lambda o: o.window[1])
    is_active = factory.LazyFunction(lambda: random.random() < 0.9)