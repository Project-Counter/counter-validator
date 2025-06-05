import logging
from io import BytesIO

import magic
from core.serializers import UserSerializerSimple
from django.conf import settings
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from .enums import ValidationStatus
from .hashing import checksum_string
from .models import CounterAPIValidation, Validation, ValidationCore, ValidationMessage

logger = logging.getLogger(__name__)


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

    error_message = serializers.CharField(read_only=True, source="core.error_message")
    file_size = serializers.IntegerField(read_only=True, source="core.file_size")
    cop_version = serializers.CharField(read_only=True, source="core.cop_version")
    api_endpoint = serializers.CharField(source="core.api_endpoint", read_only=True)
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
    requested_extra_attributes = serializers.JSONField(
        source="counterapivalidation.requested_extra_attributes", read_only=True
    )
    requested_begin_date = serializers.CharField(
        source="counterapivalidation.requested_begin_date", read_only=True
    )
    requested_end_date = serializers.CharField(
        source="counterapivalidation.requested_end_date", read_only=True
    )
    use_short_dates = serializers.BooleanField(
        read_only=True, source="counterapivalidation.use_short_dates"
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
            "public_id",
            "filename",
            "validation_result",
            "error_message",
            "file_size",
            "cop_version",
            "report_code",
            "stats",
            "api_key_prefix",
            "data_source",
            "user_note",
            # optional fields from CounterAPIValidation
            "credentials",
            "url",
            "requested_cop_version",
            "requested_report_code",
            "api_endpoint",
            "requested_extra_attributes",
            "requested_begin_date",
            "requested_end_date",
            "use_short_dates",
        ]

    def get_data_source(self, obj):
        return obj.core.sushi_credentials_checksum and "counter_api" or "file"


class ValidationDetailSerializer(ValidationSerializer):
    result_data = serializers.ReadOnlyField()
    user = UserSerializerSimple(read_only=True, source="core.user")
    full_url = serializers.SerializerMethodField()

    class Meta(ValidationSerializer.Meta):
        fields = ValidationSerializer.Meta.fields + ["result_data", "user", "full_url"]

    def get_full_url(self, obj: Validation):
        if obj.is_counter_api_validation:
            return obj.counterapivalidation.get_url()
        return ""


class ValidationWithUserSerializer(ValidationSerializer):
    user = UserSerializerSimple(read_only=True, source="core.user")

    class Meta(ValidationSerializer.Meta):
        fields = ValidationSerializer.Meta.fields + ["user"]


class PublicValidationDetailSerializer(ValidationSerializer):
    result_data = serializers.ReadOnlyField()
    credentials = serializers.SerializerMethodField()
    full_url = serializers.SerializerMethodField()

    class Meta(ValidationSerializer.Meta):
        fields = ValidationSerializer.Meta.fields + ["result_data", "full_url"]

    def get_credentials(self, obj):
        return None

    def get_full_url(self, obj: Validation):
        """
        The full URL should not be exposed for public validations.
        """
        return ""


class FileValidationCreateSerializer(serializers.Serializer):
    """
    Serializer used to create a new validation from a file upload.
    """

    file = serializers.FileField()
    user_note = serializers.CharField(required=False)
    mime_to_type = {
        "application/json": "json",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": "xlsx",
        # map all text based format to csv
        "text/csv": "csv",
        "text/tab-separated-values": "csv",
    }

    @classmethod
    def file_to_type(cls, fileobj: BytesIO):
        buffer = fileobj.read(16384)
        detected_type = magic.from_buffer(buffer, mime=True)
        if detected_type == "text/plain":
            # this can be CSV, TSV, etc., but also JSON :( - we need to make the best guess
            # ourselves
            line_number = buffer.count(b"\n") + 1
            if buffer.count(b"{") > 4:
                detected_type = "application/json"
            elif buffer.count(b",") >= line_number:
                # at least as many commas as lines, so it's a CSV
                detected_type = "text/csv"
            elif buffer.count(b"\t") >= line_number:
                # at least as many tabs as lines, so it's a TSV
                detected_type = "text/tab-separated-values"
            else:
                detected_type = "text/plain"

        logger.info(f"Detected file type: {detected_type}")
        fileobj.seek(0)
        return cls.mime_to_type.get(detected_type, "default")

    def validate_file(self, value):
        # empty files are handled by the FileField itself, so we just check the max size
        file_type = self.file_to_type(value)
        size_limit = settings.FILE_SIZE_LIMITS.get(file_type, settings.FILE_SIZE_LIMITS["default"])
        if value.size > size_limit:
            raise ValidationError(
                detail=(
                    f"Max file size for type '{file_type}' exceeded: "
                    f"{value.size} > {size_limit} bytes"
                )
            )
        return value

    def create(self, validated_data) -> Validation:
        api_key = getattr(self.context["request"], "api_key", None)
        return Validation.create_from_file(
            user=self.context["request"].user,
            file=validated_data["file"],
            user_note=validated_data.get("user_note", ""),
            api_key=api_key,
        )


class CounterAPIValidationCreateSerializer(serializers.Serializer):
    """
    Serializer to create a new COUNTER API validation from a POST request.
    """

    credentials = CredentialsSerializer(required=False, allow_null=True)
    url = serializers.URLField()
    api_endpoint = serializers.CharField(default="/reports/[id]")
    cop_version = serializers.CharField()
    report_code = serializers.CharField(allow_blank=True, required=False)
    begin_date = serializers.DateField(required=False)
    end_date = serializers.DateField(required=False)
    use_short_dates = serializers.BooleanField(default=False)
    extra_attributes = serializers.JSONField(default=dict)
    user_note = serializers.CharField(required=False, allow_blank=True)

    def validate(self, attrs):
        attrs = super().validate(attrs)
        if attrs.get("api_endpoint") == "/reports/[id]":
            for attr in ("cop_version", "begin_date", "end_date", "report_code"):
                if not attrs.get(attr):
                    raise ValidationError(f"{attr} is required if api_endpoint is /reports/[id]")
        if not attrs.get("credentials") and not (
            attrs.get("api_endpoint") == "/status" and attrs.get("cop_version") >= "5.1"
        ):
            raise ValidationError("Credentials are required for this endpoint")
        return attrs

    def create(self, validated_data) -> CounterAPIValidation:
        user = self.context["request"].user
        api_key = getattr(self.context["request"], "api_key", None)
        core = ValidationCore.objects.create(
            status=ValidationStatus.WAITING,
            user=user,
            user_email_checksum=checksum_string(user.email),
            api_key_prefix=api_key.prefix if api_key else "",
            api_endpoint=validated_data["api_endpoint"],
            cop_version=validated_data["cop_version"],
        )
        if credentials := validated_data.get("credentials"):
            if "platform" in credentials and not credentials["platform"]:
                # remove empty platform altogether
                credentials.pop("platform")
        else:
            credentials = None

        return CounterAPIValidation.objects.create(
            core=core,
            url=validated_data["url"],
            requested_cop_version=validated_data["cop_version"],
            requested_report_code=validated_data.get("report_code", ""),
            requested_begin_date=validated_data.get("begin_date"),
            requested_end_date=validated_data.get("end_date"),
            use_short_dates=validated_data.get("use_short_dates", False),
            requested_extra_attributes=validated_data["extra_attributes"],
            credentials=credentials,
            user_note=validated_data.get("user_note", ""),
        )


class ValidationCoreSerializer(serializers.ModelSerializer):
    validation_result = serializers.CharField(
        read_only=True, source="get_validation_result_display"
    )
    source = serializers.SerializerMethodField()
    user = UserSerializerSimple(read_only=True)

    class Meta:
        model = ValidationCore
        fields = (
            "id",
            "cop_version",
            "report_code",
            "status",
            "validation_result",
            "created",
            "file_size",
            "used_memory",
            "duration",
            "stats",
            "error_message",
            "source",
            "user",
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
