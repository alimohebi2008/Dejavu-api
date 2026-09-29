import random

import factory
from factory import Faker
from factory.django import DjangoModelFactory

from .models import Role, RoleType, User

# python manage.py generate_to_db accounts.UserFactory -q 20
# python manage.py generate_to_db accounts.RoleFactory -q 3


class RoleFactory(DjangoModelFactory):
    class Meta:
        model = Role
        django_get_or_create = ('name',)

    name = factory.Iterator([choice[0] for choice in RoleType.choices])


class UserFactory(DjangoModelFactory):
    class Meta:
        model = User
        django_get_or_create = ('username',)

    username = factory.Sequence(lambda n: f'user{n}')
    email = factory.Sequence(lambda n: f'user{n}@example.com')
    first_name = Faker('first_name', locale='fa_IR')
    last_name = Faker('last_name', locale='fa_IR')
    phone_number = factory.Sequence(lambda n: f'0912{n:07d}')
    password = factory.PostGenerationMethodCall('set_password', 'default123')
    is_active = True

    @factory.post_generation
    def role(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            self.role.add(*extracted)
        else:
            all_roles = list(Role.objects.all())
            if len(all_roles) < len(RoleType.choices):
                for role_type in RoleType.choices:
                    RoleFactory(name=role_type[0])
                all_roles = list(Role.objects.all())

            selected = random.sample(all_roles, random.randint(1, 2))
            self.role.add(*selected)