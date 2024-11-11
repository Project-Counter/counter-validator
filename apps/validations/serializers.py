from counter.models import Platform
from django.conf import settings
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from .models import Validation, ValidationCore


class ValidationSerializer(serializers.ModelSerializer):
    api_key = serializers.PrimaryKeyRelatedField(read_only=True)
    file = serializers.FileField(write_only=True)
    validation_result = serializers.CharField(
        read_only=True, source="core.get_validation_result_display"
    )
    status = serializers.IntegerField(read_only=True, source="core.status")
    created = serializers.DateTimeField(read_only=True, source="core.created")
    platform = serializers.SlugRelatedField(
        read_only=True, slug_field="name", source="core.platform"
    )
    platform_name = serializers.CharField(read_only=True, source="core.platform_name")
    error_message = serializers.CharField(read_only=True, source="core.error_message")

    class Meta:
        model = Validation
        fields = (
            "id",
            "api_key",
            "file",
            "status",
            "created",
            "filename",
            "platform",
            "platform_name",
            "validation_result",
            "error_message",
        )
        read_only_fields = (
            "api_key",
            "status",
            "created",
        )


class ValidationDetailSerializer(ValidationSerializer):
    result_data = serializers.ReadOnlyField()

    class Meta(ValidationSerializer.Meta):
        fields = ValidationSerializer.Meta.fields + ("result_data",)
        read_only_fields = ValidationSerializer.Meta.read_only_fields + ("result_data",)


class FileValidationCreateSerializer(serializers.Serializer):
    """
    Serializer used to create a new validation from a file upload.
    """

    file = serializers.FileField()
    platform_name = serializers.CharField(required=False)
    platform = serializers.PrimaryKeyRelatedField(queryset=Platform.objects.all(), required=False)
    user_note = serializers.CharField(required=False)

    def validate_file(self, value):
        # empty files are handled by the FileField itself, so we just check the max size
        if value.size > settings.MAX_FILE_SIZE:
            raise ValidationError(
                detail=(
                    f"Max file size exceeded: " f"{value.size} > {settings.MAX_FILE_SIZE} bytes"
                )
            )
        return value

    def create(self, validated_data) -> Validation:
        platform = validated_data.get("platform")
        return Validation.create_from_file(
            user=self.context["request"].user,
            file=validated_data["file"],
            platform=platform,
            platform_name=platform.name if platform else validated_data.get("platform_name", ""),
            user_note=validated_data.get("user_note", ""),
        )


class ValidationCoreSerializer(serializers.ModelSerializer):
    platform_name = serializers.CharField(source="platform.name", read_only=True)
    validation_result = serializers.CharField(
        read_only=True, source="get_validation_result_display"
    )

    class Meta:
        model = ValidationCore
        fields = (
            "id",
            "cop_version",
            "report_code",
            "status",
            "platform",
            "platform_name",
            "validation_result",
            "created",
            "file_size",
            "used_memory",
            "duration",
            "stats",
            "error_message",
        )
        read_only_fields = fields
