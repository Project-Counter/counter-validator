import typing

import rest_framework.permissions
from django.http import HttpRequest
from rest_framework.permissions import BasePermission


class IsAuthenticatedForListOrCreateAnyForDetail(BasePermission):
    def has_permission(self, request: HttpRequest, view: typing.Any) -> bool:
        if view.detail and request.method in rest_framework.permissions.SAFE_METHODS:
            return True
        return request.user.is_authenticated


class IsValidationOwnerOrIsPublic(BasePermission):
    def has_object_permission(
        self, request: HttpRequest, view: typing.Any, obj: typing.Any
    ) -> bool:
        return obj.public_id is not None or obj.core.user == request.user
