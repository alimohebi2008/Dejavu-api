import random
import uuid
from decimal import Decimal

import factory
from factory import Faker
from factory.django import DjangoModelFactory
from faker import Faker as FakerLib

from .models import Category, Product, ProductSize

# python manage.py generate_to_db products.CategoryFactory -q 8
# python manage.py generate_to_db products.ProductSizeFactory -q 6
# python manage.py generate_to_db products.ProductFactory -q 40

fake = FakerLib('fa_IR')


SIZES = [
    (100, 150),
    (120, 180),
    (150, 200),
    (200, 300),
    (250, 350),
    (300, 400),
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