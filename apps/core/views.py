import logging

from rest_framework import mixins, status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from . import serializers
from .models import UserApiKey

logger = logging.getLogger(__name__)


class UserApiKeyViewSet(mixins.RetrieveModelMixin, mixins.ListModelMixin, GenericViewSet):
    lookup_field = "prefix"
    serializer_class = serializers.UserApiKeySerializer

    def get_queryset(self):
        return self.request.user.userapikey_set

    def create(self, request, *_, **__):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        _, key = UserApiKey.objects.create_key(**serializer.validated_data, user=self.request.user)
        return Response({"key": key}, status=status.HTTP_201_CREATED)

    def destroy(self, *_, **__):
        obj = self.get_object()
        if obj.revoked:
            raise ValidationError(detail="This API key has already been revoked")
        obj.revoked = True
        obj.save()
        return Response(self.get_serializer(obj).data)
