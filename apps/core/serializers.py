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
