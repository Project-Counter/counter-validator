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
	# todo sushi_services = serializers.HyperlinkedRelatedField(many=True, read_only=True, view_name="")
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


class FileValidationSerializer(serializers.ModelSerializer):
	status = serializers.ReadOnlyField()
	created = serializers.ReadOnlyField()
	headers = serializers.ReadOnlyField()
	messages = serializers.ReadOnlyField()
	memory = serializers.ReadOnlyField()

	platform = serializers.PrimaryKeyRelatedField(read_only=True)
	file = serializers.FileField(write_only=True)

	class Meta:
		model = models.FileValidation
		fields = (
			"id",
			"status",
			"created",
			"file",
			"filename",
			"headers",
			"messages",
			"memory",
			"platform",
			"platform_name",
		)
