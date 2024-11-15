from counter.models import Platform
from django.conf import settings
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from .enums import ValidationStatus
from .hashing import checksum_string
from .models import CounterAPIValidation, Validation, ValidationCore


class ValidationSerializer(serializers.ModelSerializer):
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
    file_size = serializers.IntegerField(read_only=True, source="core.file_size")
    cop_version = serializers.CharField(read_only=True, source="core.cop_version")
    report_code = serializers.CharField(read_only=True, source="core.report_code")
    stats = serializers.JSONField(read_only=True, source="core.stats")
    api_key_prefix = serializers.CharField(read_only=True, source="core.api_key_prefix")

    class Meta:
        model = Validation
        fields = [
            "id",
            "file",
            "status",
            "created",
            "filename",
            "platform",
            "platform_name",
            "validation_result",
            "error_message",
            "file_size",
            "cop_version",
            "report_code",
            "stats",
            "api_key_prefix",
        ]


class ValidationDetailSerializer(ValidationSerializer):
    result_data = serializers.ReadOnlyField()

    class Meta(ValidationSerializer.Meta):
        fields = ValidationSerializer.Meta.fields + ["result_data"]


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
        api_key = getattr(self.context["request"], "api_key", None)
        return Validation.create_from_file(
            user=self.context["request"].user,
            file=validated_data["file"],
            platform=platform,
            platform_name=platform.name if platform else validated_data.get("platform_name", ""),
            user_note=validated_data.get("user_note", ""),
            api_key=api_key,
        )


class CounterAPIValidationSerializer(ValidationSerializer):
    class Meta:
        model = CounterAPIValidation
        fields = ValidationSerializer.Meta.fields + [
            "url",
            "requested_cop_version",
            "requested_report_code",
            "requested_begin_date",
            "requested_end_date",
            "requested_extra_attributes",
            "credentials",
            "api_endpoint",
        ]


class CredentialsSerializer(serializers.Serializer):
    requestor_id = serializers.CharField()
    customer_id = serializers.CharField()
    api_key = serializers.CharField()


class CounterAPIValidationCreateSerializer(serializers.Serializer):
    """
    Serializer to create a new COUNTER API validation from a POST request.
    """

    credentials = CredentialsSerializer()
    url = serializers.URLField()
    cop_version = serializers.CharField()
    report_code = serializers.CharField()
    begin_date = serializers.DateField()
    end_date = serializers.DateField()
    extra_attributes = serializers.JSONField(default=dict)

    def create(self, validated_data) -> CounterAPIValidation:
        user = self.context["request"].user
        api_key = getattr(self.context["request"], "api_key", None)
        core = ValidationCore.objects.create(
            status=ValidationStatus.WAITING,
            user_email_checksum=checksum_string(user.email),
            api_key_prefix=api_key.prefix if api_key else "",
        )

        return CounterAPIValidation.objects.create(
            core=core,
            user=user,
            url=validated_data["url"],
            requested_cop_version=validated_data["cop_version"],
            requested_report_code=validated_data["report_code"],
            requested_begin_date=validated_data["begin_date"],
            requested_end_date=validated_data["end_date"],
            requested_extra_attributes=validated_data["extra_attributes"],
            credentials=validated_data["credentials"],
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
