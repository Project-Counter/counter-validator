from rest_framework import serializers

from . import models


class UserApiKeySerializer(serializers.ModelSerializer):
    name = serializers.CharField(required=True, max_length=50)
    has_expired = serializers.BooleanField(source="_has_expired", read_only=True)

    class Meta:
        model = models.UserApiKey
        fields = (
            "prefix",
            "created",
            "name",
            "revoked",
            "expiry_date",
            "has_expired",
        )


class SushiServiceSerializer(serializers.ModelSerializer):
    deprecated = serializers.ReadOnlyField()

    class Meta:
        model = models.SushiService
        fields = (
            "id",
            "counter_release",
            "url",
            "ip_address_authorization",
            "api_key_required",
            "platform_attr_required",
            "requestor_id_required",
            "deprecated",
        )


class ReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Report
        fields = (
            "counter_release",
            "report_id",
        )


class PlatformSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Platform
        fields = (
            "id",
            "name",
            "abbrev",
            "deprecated",
        )


class PlatformSerializer(serializers.ModelSerializer):
    reports = ReportSerializer(many=True, read_only=True)
    sushi_services = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    deprecated = serializers.ReadOnlyField()

    class Meta:
        model = models.Platform
        fields = (
            "id",
            "name",
            "abbrev",
            "reports",
            "content_provider_name",
            "website",
            "sushi_services",
            "deprecated",
        )


class ValidationSerializer(serializers.ModelSerializer):
    api_key = serializers.PrimaryKeyRelatedField(read_only=True)
    platform = serializers.SlugRelatedField(read_only=True, slug_field="name")
    file = serializers.FileField(write_only=True)

    class Meta:
        model = models.Validation
        fields = (
            "id",
            "api_key",
            "file",
            "status",
            "created",
            "filename",
            "platform",
            "platform_name",
        )
        read_only_fields = (
            "api_key",
            "status",
            "created",
        )


class ValidationDetailSerializer(ValidationSerializer):
    result = serializers.ReadOnlyField()

    class Meta(ValidationSerializer.Meta):
        fields = ValidationSerializer.Meta.fields + ("result",)
        read_only_fields = ValidationSerializer.Meta.read_only_fields + ("result",)


class Credentials(serializers.Serializer):
    url = serializers.CharField(max_length=250)
    platform = serializers.CharField(max_length=250, allow_blank=True)
    customer_id = serializers.CharField(max_length=250)
    requestor_id = serializers.CharField(max_length=250, allow_blank=True)
    api_key = serializers.CharField(max_length=250, allow_blank=True)
