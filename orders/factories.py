import random
import uuid

import factory
from django.contrib.auth import get_user_model
from factory.django import DjangoModelFactory

from accounts.factories import UserFactory
from products.factories import ProductFactory
from products.models import Product

from .models import Cart, CartItem, Order, OrderItem

# python manage.py generate_to_db accounts.UserFactory -q 20
# python manage.py generate_to_db products.ProductFactory -q 40
# python manage.py generate_to_db orders.CartFactory -q 10
# python manage.py generate_to_db orders.OrderFactory -q 30

User = get_user_model()


def new_user():
    return UserFactory(username=f'user_{uuid.uuid4().hex[:8]}', phone_number=None)


def random_user():
    return User.objects.order_by('?').first() or new_user()


def user_without_cart():
    return User.objects.filter(cart__isnull=True).order_by('?').first() or new_user()


def random_products(k):
    if Product.objects.count() < 10:
        ProductFactory.create_batch(10)
    products = list(Product.objects.all())
    return random.sample(products, min(k, len(products)))


def random_product():
    return random_products(1)[0]


# ---------- cart ----------

class CartFactory(DjangoModelFactory):
    class Meta:
        model = Cart
        skip_postgeneration_save = True

    user = factory.LazyFunction(user_without_cart)

    @factory.post_generation
    def items(self, create, extracted, **kwargs):
        if not create:
            return

        for product in random_products(random.randint(1, 4)):
            CartItemFactory(cart=self, product=product)


class CartItemFactory(DjangoModelFactory):
    class Meta:
        model = CartItem
        django_get_or_create = ('cart', 'product')

    cart = factory.LazyFunction(lambda: Cart.objects.order_by('?').first() or CartFactory())
    product = factory.LazyFunction(random_product)
    quantity = factory.LazyFunction(lambda: random.randint(1, 3))


# ---------- order ----------

class OrderFactory(DjangoModelFactory):
    class Meta:
        model = Order
        skip_postgeneration_save = True

    user = factory.LazyFunction(random_user)
    status = factory.LazyFunction(lambda: random.choice(Order.Status.values))

    @factory.post_generation
    def items(self, create, extracted, **kwargs):
        if not create:
            return

        for product in random_products(random.randint(1, 4)):
            OrderItemFactory(order=self, product=product)


class OrderItemFactory(DjangoModelFactory):
    class Meta:
        model = OrderItem
        django_get_or_create = ('order', 'product')
        skip_postgeneration_save = True

    order = factory.LazyFunction(lambda: Order.objects.order_by('?').first() or OrderFactory())
    product = factory.LazyFunction(random_product)
    quantity = factory.LazyFunction(lambda: random.randint(1, 3))
    price = factory.LazyAttribute(lambda o: o.product.price)  # قیمت لحظه‌ی خرید

    @factory.post_generation
    def update_total(self, create, extracted, **kwargs):
        if create:
            self.order.recalculate_total()
