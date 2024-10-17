# Create your views here.
from core.tasks import validate_file, validate_sushi
from core.views import logger
from counter.models import Platform
from counter.serializers import Credentials
from django.conf import settings
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.parsers import FileUploadParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet

import validations.serializers
from validations.models import Validation


class ValidationViewSet(ReadOnlyModelViewSet):
    permission_classes = (IsAuthenticated,)
    serializer_class = validations.serializers.ValidationSerializer

    def get_serializer_class(self):
        if self.action == "list":
            return validations.serializers.ValidationSerializer
        return validations.serializers.ValidationDetailSerializer

    def get_queryset(self):
        qs = self.request.user.validation_set.defer("result_data")
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

    @action(detail=False, methods=("POST",))
    def sushi(self, request):
        obj = Validation.objects.create(
            user=request.user,
            status=Validation.StatusEnum.WAITING,
        )
        serializer = Credentials(data=request.data)
        serializer.is_valid(raise_exception=True)
        validate_sushi.delay_on_commit(obj.pk, serializer.validated_data)
        return Response(status=status.HTTP_201_CREATED)
