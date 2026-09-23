from django.db import models

class RoleType(models.TextChoices):
    ADMIN = "admin", "ادمین"
    USER = "user", "کاربر"
    STAFF = "staff", "پرسنل"

class Role(models.Model):
    name = models.CharField(max_length=50, verbose_name='نوع نقش', unique=True, choices=RoleType.choices,
                            default=RoleType.PROGRAMMER)

    class Meta:
        verbose_name = 'نوع نقش'
        verbose_name_plural = 'نوع نقش ها'

    def __str__(self):
        return self.name

class User(AbstractUser):
    role = models.ManyToManyField("Role", verbose_name='نقش ها')
    phone_number = models.CharField(max_length=15, verbose_name='تلفن همراه', validators=[PhoneNumbersValidator],
                                    null=True, blank=True, unique=True)
    image = models.ImageField(upload_to='users_image', null=True, blank=True, verbose_name='تصویر کابر')

