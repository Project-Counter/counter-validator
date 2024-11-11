# Create your views here.
from core.tasks import validate_file, validate_sushi
from counter.serializers import Credentials
from django.db.transaction import atomic
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.mixins import DestroyModelMixin
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet

import validations.serializers
from validations.enums import ValidationStatus
from validations.models import Validation, ValidationCore
from validations.serializers import FileValidationCreateSerializer


class ValidationViewSet(DestroyModelMixin, ReadOnlyModelViewSet):
    permission_classes = (IsAuthenticated,)
    serializer_class = validations.serializers.ValidationSerializer

    def get_serializer_class(self):
        if self.action == "list":
            return validations.serializers.ValidationSerializer
        return validations.serializers.ValidationDetailSerializer

    def get_queryset(self):
        qs = (
            self.request.user.validation_set.select_related("core")
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
        # sleep(2)
        return Response(out_serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=("POST",))
    def sushi(self, request):
        obj = Validation.objects.create(
            user=request.user,
            status=ValidationStatus.WAITING,
        )
        serializer = Credentials(data=request.data)
        serializer.is_valid(raise_exception=True)
        validate_sushi.delay_on_commit(obj.pk, serializer.validated_data)
        return Response(status=status.HTTP_201_CREATED)


class ValidationCoreViewSet(ReadOnlyModelViewSet):
    permission_classes = (IsAdminUser,)
    serializer_class = validations.serializers.ValidationCoreSerializer

    def get_queryset(self):
        return ValidationCore.objects.select_related("platform").order_by("-created")
