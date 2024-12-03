from counter.models import Platform
from django.conf import settings
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from .enums import ValidationStatus
from .hashing import checksum_string
from .models import CounterAPIValidation, Validation, ValidationCore, ValidationMessage


class CredentialsSerializer(serializers.Serializer):
    requestor_id = serializers.CharField(required=False, allow_blank=True)
    customer_id = serializers.CharField()
    api_key = serializers.CharField(required=False, allow_blank=True)
    platform = serializers.CharField(required=False, allow_blank=True, allow_null=True)


class ValidationSerializer(serializers.ModelSerializer):
    file = serializers.FileField(write_only=True)
    file_url = serializers.URLField(read_only=True)
    validation_result = serializers.CharField(
        read_only=True, source="core.get_validation_result_display"
    )
    status = serializers.IntegerField(read_only=True, source="core.status")
    created = serializers.DateTimeField(read_only=True, source="core.created")
    expiration_date = serializers.DateTimeField(read_only=True, source="core.expiration_date")

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
    data_source = serializers.SerializerMethodField()
    # attrs from optional counterapivalidation
    credentials = CredentialsSerializer(source="counterapivalidation.credentials", read_only=True)
    url = serializers.CharField(source="counterapivalidation.url", read_only=True)
    requested_cop_version = serializers.CharField(
        source="counterapivalidation.requested_cop_version", read_only=True
    )
    requested_report_code = serializers.CharField(
        source="counterapivalidation.requested_report_code", read_only=True
    )
    api_endpoint = serializers.CharField(source="counterapivalidation.api_endpoint", read_only=True)
    requested_extra_attributes = serializers.JSONField(
        source="counterapivalidation.requested_extra_attributes", read_only=True
    )
    requested_begin_date = serializers.CharField(
        source="counterapivalidation.requested_begin_date", read_only=True
    )
    requested_end_date = serializers.CharField(
        source="counterapivalidation.requested_end_date", read_only=True
    )

    class Meta:
        model = Validation
        fields = [
            "id",
            "file",
            "file_url",
            "status",
            "created",
            "expiration_date",
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
            "data_source",
            # optional fields from CounterAPIValidation
            "credentials",
            "url",
            "requested_cop_version",
            "requested_report_code",
            "api_endpoint",
            "requested_extra_attributes",
            "requested_begin_date",
            "requested_end_date",
        ]

    def get_data_source(self, obj):
        try:
            return obj.counterapivalidation and "counter_api"
        except CounterAPIValidation.DoesNotExist:
            return "file"


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


class CounterAPIValidationCreateSerializer(serializers.Serializer):
    """
    Serializer to create a new COUNTER API validation from a POST request.
    """

    credentials = CredentialsSerializer()
    url = serializers.URLField()
    api_endpoint = serializers.CharField(default="/reports/[id]")
    cop_version = serializers.CharField()
    report_code = serializers.CharField(allow_blank=True, required=False)
    begin_date = serializers.DateField(required=False)
    end_date = serializers.DateField(required=False)
    extra_attributes = serializers.JSONField(default=dict)

    def validate(self, attrs):
        attrs = super().validate(attrs)
        if attrs.get("api_endpoint") == "/reports/[id]":
            for attr in ("cop_version", "begin_date", "end_date", "report_code"):
                if not attrs.get(attr):
                    raise ValidationError(f"{attr} is required if api_endpoint is /reports/[id]")
        return attrs

    def create(self, validated_data) -> CounterAPIValidation:
        user = self.context["request"].user
        api_key = getattr(self.context["request"], "api_key", None)
        core = ValidationCore.objects.create(
            status=ValidationStatus.WAITING,
            user_email_checksum=checksum_string(user.email),
            api_key_prefix=api_key.prefix if api_key else "",
        )
        credentials = validated_data["credentials"]
        if "platform" in credentials and not credentials["platform"]:
            # remove empty platform altogether
            credentials.pop("platform")

        return CounterAPIValidation.objects.create(
            core=core,
            user=user,
            url=validated_data["url"],
            api_endpoint=validated_data["api_endpoint"],
            requested_cop_version=validated_data["cop_version"],
            requested_report_code=validated_data.get("report_code", ""),
            requested_begin_date=validated_data.get("begin_date"),
            requested_end_date=validated_data.get("end_date"),
            requested_extra_attributes=validated_data["extra_attributes"],
            credentials=credentials,
        )


class ValidationCoreSerializer(serializers.ModelSerializer):
    platform_name = serializers.CharField(source="platform.name", read_only=True)
    validation_result = serializers.CharField(
        read_only=True, source="get_validation_result_display"
    )
    source = serializers.SerializerMethodField()

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
            "source",
        )
        read_only_fields = fields

    @classmethod
    def get_source(cls, obj: ValidationCore):
        return "counter_api" if obj.sushi_credentials_checksum else "file"


class ValidationMessageSerializer(serializers.ModelSerializer):
    severity = serializers.CharField(source="get_severity_display", read_only=True)

    class Meta:
        model = ValidationMessage
        fields = ("severity", "code", "message", "location", "summary", "hint", "data")
        read_only_fields = fields
