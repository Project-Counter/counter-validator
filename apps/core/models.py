from django.conf import settings
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import AbstractUser
from django.db import models
from rest_framework_api_key.crypto import KeyGenerator
from rest_framework_api_key.models import AbstractAPIKey, BaseAPIKeyManager


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError("Email must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.password = make_password(password)
        user.save()
        return user

    def create_user(self, email, password=None, **extra_fields):
        """
        Alternative implementation of create_user which does not require username
        """
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        """
        Alternative implementation of create_superuser which does not require username
        """
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(email, password, **extra_fields)


class User(AbstractUser):
    objects = UserManager()

    username_validator = None
    username = None
    email = models.EmailField(unique=True)
    is_validator_admin = models.BooleanField(default=False)
    receive_operator_emails = models.BooleanField(
        default=False,
        help_text="Whether this user should receive operator emails. Only relevant for admins.",
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ()

    @property
    def has_admin_role(self):
        return self.is_superuser or self.is_validator_admin

    @property
    def verified_email(self):
        if hasattr(self, "_verified_email"):
            # the value was provided in the queryset as an annotation
            return self._verified_email
        return self.emailaddress_set.filter(verified=True, email=self.email).exists()


class UserApiKeyManager(BaseAPIKeyManager):
    key_generator = KeyGenerator(prefix_length=8, secret_key_length=48)


class UserApiKey(AbstractAPIKey):
    objects = UserApiKeyManager()

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
