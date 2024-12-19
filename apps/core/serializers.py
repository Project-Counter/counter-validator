from dj_rest_auth.registration.serializers import RegisterSerializer
from rest_framework import serializers

from . import models
from .models import User


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


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.User

        fields = (
            "id",
            "email",
            "first_name",
            "last_name",
            "is_validator_admin",
            "is_superuser",
            "is_active",
        )


class ValidatorRegisterSerializer(RegisterSerializer):
    def validate_email(self, email):
        email = super().validate_email(email)
        if email and User.objects.filter(email=email).exists():
            raise serializers.ValidationError(
                "A user is already registered with this e-mail address."
            )
        return email
