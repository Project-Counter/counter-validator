from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from rest_framework_api_key.models import APIKey

from core.models import User

admin.site.unregister(APIKey)


@admin.register(User)
class MyUserAdmin(UserAdmin):
    list_display = (
        "email",
        "first_name",
        "last_name",
        "last_login",
        "is_validator_admin",
        "is_active",
        "is_staff",
    )

    ordering = (User.USERNAME_FIELD,)

    fields = (
        "email",
        "first_name",
        "last_name",
        "is_validator_admin",
        "is_active",
        "is_staff",
        "is_superuser",
        "groups",
        "user_permissions",
    )
    fieldsets = None  # unset the default fieldsets

    search_fields = ("email", "first_name", "last_name")
