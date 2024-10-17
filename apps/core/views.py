import logging

from django.conf import settings
from rest_framework import mixins, status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.parsers import FileUploadParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet, ReadOnlyModelViewSet

from . import serializers
from .models import Platform, SushiService, UserApiKey, Validation
from .serializers import Credentials
from .tasks import validate_file, validate_sushi


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


class ValidationViewSet(ReadOnlyModelViewSet):
    permission_classes = (IsAuthenticated,)
    serializer_class = serializers.ValidationSerializer

    def get_queryset(self):
        qs = self.request.user.validation_set.defer("result")
        if self.action not in ("sushi", "file"):
            qs = qs.prefetch_related("platform")
        if self.action == "detail":
            qs = qs.defer(None)
        return qs

    @action(
        detail=False,
        parser_classes=(FileUploadParser,),
        methods=("POST",),
        url_path=r"file/(?P<filename>[^/]+)",
    )
    def file(self, request, filename):
        platform_name = request.query_params.get("platform_name", "")
        platform = None
        try:
            # TODO: use registry id in the background instead of name
            platform = Platform.objects.get(name=platform_name)
            platform_name = ""
        except Platform.DoesNotExist:
            pass

        if "file" not in request.data:
            raise ValidationError(detail="Empty files are not supported")
        logger.info("File size: %d", request.data["file"].size)
        if request.data["file"].size > settings.MAX_FILE_SIZE:
            raise ValidationError(
                detail=(
                    f"Max file size exceeded: "
                    f"{request.data['file'].size} > {settings.MAX_FILE_SIZE} bytes"
                )
            )

        data = request.data
        data["filename"] = request.data["file"].name
        data["platform_name"] = platform_name
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        obj = serializer.save(
            user=request.user,
            status=Validation.StatusEnum.WAITING,
            platform=platform,
        )
        validate_file.delay_on_commit(obj.pk)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(
        detail=True,
    )
    def details(self, request, pk):
        serializer = serializers.ValidationDetailSerializer(self.get_object())
        return Response(serializer.data)

    @action(
        detail=False,
        methods=("POST",),
    )
    def sushi(self, request):
        obj = Validation.objects.create(
            user=request.user,
            status=Validation.StatusEnum.WAITING,
        )
        serializer = Credentials(data=request.data)
        serializer.is_valid(raise_exception=True)
        validate_sushi.delay_on_commit(obj.pk, serializer.validated_data)
        return Response(status=status.HTTP_201_CREATED)


class PlatformViewSet(ReadOnlyModelViewSet):
    permission_classes = (IsAuthenticated,)

    def get_serializer_class(self):
        if self.action == "list":
            return serializers.PlatformSimpleSerializer
        return serializers.PlatformSerializer

    def get_queryset(self):
        qs = Platform.objects.all()
        if self.action == "detail":
            qs = qs.prefetch_related("reports", "sushi_services")
        return qs


class SushiServiceViewSet(ReadOnlyModelViewSet):
    permission_classes = (IsAuthenticated,)

    def get_serializer_class(self):
        if self.action == "list":
            return serializers.SushiServiceSerializer
        return serializers.SushiServiceSerializer

    def get_queryset(self):
        qs = SushiService.objects.all()
        # if self.action == "detail":
        # 	qs = qs.prefetch_related("reports", "sushi_services")
        return qs
