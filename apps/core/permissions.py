import typing

from django.http import HttpRequest
from rest_framework.permissions import BasePermission
from rest_framework_api_key.permissions import BaseHasAPIKey

from core.models import UserApiKey


class HasUserAPIKey(BaseHasAPIKey):
    model = UserApiKey

    def has_permission(self, request: HttpRequest, view: typing.Any) -> bool:
        """
        Based on upstream implementation, but with a custom model.
        """
        key = self.get_key(request)
        if not key:
            return False
        if self.model.objects.is_valid(key):
            api_key = self.model.objects.get_from_key(key)
            request.user = api_key.user
            request.api_key = api_key
            return True
        return False


class IsValidatorAdminUser(BasePermission):
    def has_permission(self, request: HttpRequest, view: typing.Any) -> bool:
        return request.user.is_authenticated and (
            request.user.is_superuser or request.user.is_validator_admin
        )
