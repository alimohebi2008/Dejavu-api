from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Role, User


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)
    list_filter = ("name",)


@admin.register(User)
class UserAdmin(UserAdmin):
    list_display = (
        "username",
        "first_name",
        "last_name",
        "phone_number",
        "is_active",
        "is_staff",
    )
    search_fields = (
        "username",
        "first_name",
        "last_name",
        "phone_number",
    )
    list_filter = (
        "is_active",
        "is_staff",
        "is_superuser",
        "role",
    )
    filter_horizontal = ("role",)

    fieldsets = UserAdmin.fieldsets + (
        (
            "اطلاعات اضافی",
            {
                "fields": (
                    "role",
                    "phone_number",
                    "image",
                )
            },
        ),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        (
            "اطلاعات اضافی",
            {
                "fields": (
                    "role",
                    "phone_number",
                    "image",
                )
            },
        ),
    )