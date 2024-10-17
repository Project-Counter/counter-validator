from rest_framework import serializers

import validations.models


class ValidationSerializer(serializers.ModelSerializer):
    api_key = serializers.PrimaryKeyRelatedField(read_only=True)
    platform = serializers.SlugRelatedField(read_only=True, slug_field="name")
    file = serializers.FileField(write_only=True)
    validation_result = serializers.CharField(
        read_only=True, source="get_validation_result_display"
    )

    class Meta:
        model = validations.models.Validation
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
