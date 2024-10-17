from django.contrib import admin
from rest_framework_api_key.models import APIKey

from . import models

admin.site.unregister(APIKey)


@admin.register(models.Validation)
class ValidationAdmin(admin.ModelAdmin):
    list_display = ["id", "created", "user", "status", "validation_result"]
    list_filter = ["status", "validation_result", "user"]
    search_fields = ["user__email"]
