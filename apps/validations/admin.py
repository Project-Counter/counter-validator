from django.contrib import admin

from . import models


@admin.register(models.ValidationCore)
class ValidationCoreAdmin(admin.ModelAdmin):
    list_display = ["id", "created", "user", "status", "validation_result"]
    list_filter = ["status", "user", "validation_result"]


@admin.register(models.Validation)
class ValidationAdmin(admin.ModelAdmin):
    list_display = ["id", "core__user", "core__status", "core__validation_result"]
    list_filter = ["core__status", "core__validation_result", "core__user"]
    search_fields = ["user__email"]

    list_select_related = ["core"]
