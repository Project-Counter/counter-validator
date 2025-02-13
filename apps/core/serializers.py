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
    verified_email = serializers.BooleanField(read_only=True)

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
            "has_admin_role",
            "last_login",
            "verified_email",
        )

    def update(self, instance, validated_data):
        request = self.context.get("request")
        if request and request.user == instance:
            # remove some fields if the user is updating themselves
            validated_data.pop("is_validator_admin", None)
            validated_data.pop("is_superuser", None)
            validated_data.pop("is_active", None)
        return super().update(instance, validated_data)


class ValidatorRegisterSerializer(RegisterSerializer):
    first_name = serializers.CharField(required=False, write_only=True)
    last_name = serializers.CharField(required=False, write_only=True)

    def validate_email(self, email):
        email = super().validate_email(email)
        if email and User.objects.filter(email=email).exists():
            raise serializers.ValidationError(
                "A user is already registered with this e-mail address."
            )
        return email

    def save(self, request):
        user = super().save(request)
        user.first_name = self.validated_data.get("first_name", "")
        user.last_name = self.validated_data.get("last_name", "")
        user.save()
        return user
