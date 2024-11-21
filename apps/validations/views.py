from core.permissions import HasUserAPIKey
from django.db.transaction import atomic
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.mixins import DestroyModelMixin
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

import validations.serializers
from validations.models import Validation, ValidationCore, ValidationMessage
from validations.serializers import (
    CounterAPIValidationCreateSerializer,
    FileValidationCreateSerializer,
)
from validations.tasks import validate_counter_api, validate_file


class ValidationViewSet(DestroyModelMixin, ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated | HasUserAPIKey]
    serializer_class = validations.serializers.ValidationSerializer

    def get_serializer_class(self):
        if self.action == "list":
            return validations.serializers.ValidationSerializer
        return validations.serializers.ValidationDetailSerializer

    def get_queryset(self):
        qs = (
            self.request.user.validation_set.select_related("core")
            .prefetch_related("counterapivalidation")
            .defer("result_data")
            .order_by("-core__created")
        )
        if self.action not in ("sushi", "file"):
            qs = qs.select_related("core__platform")
        if self.action == "detail":
            qs = qs.defer(None)
        return qs

    @action(detail=False, methods=("POST",), url_path="file")
    @atomic
    def file(self, request):
        serializer = FileValidationCreateSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        obj = serializer.save()
        validate_file.delay_on_commit(obj.pk)
        out_serializer = self.get_serializer(obj)
        return Response(out_serializer.data, status=status.HTTP_201_CREATED)


class CounterAPIValidationViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated | HasUserAPIKey]
    serializer_class = validations.serializers.CounterAPIValidationSerializer

    def create(self, request, *args, **kwargs):
        serializer = CounterAPIValidationCreateSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        obj = serializer.save()
        validate_counter_api.delay_on_commit(obj.pk)
        out_serializer = self.get_serializer(obj)
        return Response(out_serializer.data, status=status.HTTP_201_CREATED)


class ValidationCoreViewSet(ReadOnlyModelViewSet):
    permission_classes = (IsAdminUser,)
    serializer_class = validations.serializers.ValidationCoreSerializer

    def get_queryset(self):
        return ValidationCore.objects.select_related("platform").order_by("-created")


class ValidationMessageViewSet(ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = validations.serializers.ValidationMessageSerializer
    pagination_class = PageNumberPagination

    def get_queryset(self):
        validation = get_object_or_404(
            Validation.objects.filter(user=self.request.user), pk=self.kwargs["validation_pk"]
        )
        return ValidationMessage.objects.filter(validation=validation)
