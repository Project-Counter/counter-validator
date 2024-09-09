from django.conf import settings
from rest_framework import mixins, status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.parsers import FileUploadParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet, ReadOnlyModelViewSet

from . import serializers
from .models import FileValidation, Platform, UserApiKey
from .tasks import validate_file


class UserApiKeyViewSet(mixins.RetrieveModelMixin, mixins.ListModelMixin, GenericViewSet):
	lookup_field = "prefix"
	serializer_class = serializers.UserApiKeySerializer

	def get_queryset(self):
		return self.request.user.userapikey_set

	def create(self, request, *args, **kwargs):
		serializer = self.get_serializer(data=request.data)
		serializer.is_valid(raise_exception=True)
		_, key = UserApiKey.objects.create_key(**serializer.validated_data, user=self.request.user)
		return Response({"key": key}, status=status.HTTP_201_CREATED)

	def destroy(self, request, *args, **kwargs):
		obj = self.get_object()
		if obj.revoked:
			raise ValidationError(detail="This API key has already been revoked")
		obj.revoked = True
		obj.save()
		return Response(self.get_serializer(obj).data, status=status.HTTP_200_OK)


class ValidationViewSet(ReadOnlyModelViewSet):
	permission_classes = (IsAuthenticated,)
	queryset = FileValidation.objects.all()
	serializer_class = serializers.FileValidationSerializer

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
			platform = Platform.objects.get(name=platform_name)  # FIXME: name not unique!
			platform_name = ""
		except Platform.DoesNotExist:
			pass

		data = request.data
		data["filename"] = request.data["file"].name
		data["platform_name"] = platform_name
		serializer = self.get_serializer(data=data)

		if "file" not in request.data:
			raise ValidationError(detail="Empty files are not supported")
		if request.data["file"].size > settings.MAX_FILE_SIZE:
			raise ValidationError(
				detail=(
					f"Max file size exceeded: "
					f"{request.data["file"].size} > {settings.MAX_FILE_SIZE} bytes"
				)
			)
		serializer.is_valid(raise_exception=True)
		obj = serializer.save(
			user=request.user,
			status=FileValidation.StatusEnum.WAITING,
			platform=platform,
		)
		# obj = FileValidation.objects.create(
		# 	user=request.user,
		# 	status=FileValidation.StatusEnum.WAITING,
		# 	filename=request.data["file"].name,
		# 	file=request.data["file"],
		# )
		validate_file.delay_on_commit(obj.pk)
		return Response(serializer.data, status=status.HTTP_201_CREATED)


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
