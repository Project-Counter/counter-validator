from django.contrib import admin
from rest_framework_api_key.models import APIKey

admin.site.unregister(APIKey)
