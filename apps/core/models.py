import os
import string

from django.conf import settings
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.crypto import get_random_string
from django.utils.timezone import now
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
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
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

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ()


class UserApiKeyManager(BaseAPIKeyManager):
    key_generator = KeyGenerator(prefix_length=8, secret_key_length=48)


class UserApiKey(AbstractAPIKey):
    objects = UserApiKeyManager()

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)


class Report(models.Model):
    counter_release = models.CharField(max_length=20)
    report_id = models.CharField(max_length=20, primary_key=True)

    def __str__(self):
        return f"{self.report_id} (C{self.counter_release})"


class Platform(models.Model):
    id = models.UUIDField(primary_key=True)
    name = models.CharField(max_length=400)
    abbrev = models.CharField(max_length=50, blank=True)
    content_provider_name = models.CharField(max_length=400, blank=True)
    website = models.URLField(blank=True)
    reports = models.ManyToManyField(Report, through="ReportToPlatform", related_name="platforms")
    deprecated = models.BooleanField(default=False)

    def __str__(self):
        if self.abbrev:
            return f"{self.name} ({self.abbrev})"
        else:
            return self.name

    @property
    def registry_url(self):
        return f"{settings.REGISTRY_URL}/platform/{self.pk}"


class ReportToPlatform(models.Model):
    report = models.ForeignKey(Report, on_delete=models.CASCADE)
    platform = models.ForeignKey(Platform, on_delete=models.CASCADE)

    def __str__(self):
        return type(self).__name__


class SushiService(models.Model):
    id = models.UUIDField(primary_key=True)
    counter_release = models.CharField(max_length=20)
    url = models.URLField(blank=True)
    platform = models.ForeignKey(
        Platform, on_delete=models.SET_NULL, related_name="sushi_services", null=True
    )
    ip_address_authorization = models.BooleanField(
        null=True, blank=True, help_text="Access restricted based on IP address"
    )
    api_key_required = models.BooleanField(null=True, blank=True, help_text="Is api key required")
    platform_attr_required = models.BooleanField(
        null=True, blank=True, help_text="Is platform attr required"
    )
    requestor_id_required = models.BooleanField(
        null=True, blank=True, help_text="Is requestor_id required"
    )
    deprecated = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.url or ''} (C{self.counter_release})"


def validation_upload_to(instance: "Validation", filename):
    _root, ext = os.path.splitext(filename)
    random_suffix = get_random_string(8, string.ascii_letters + string.digits)
    ts = now().strftime("%Y%m%d-%H%M%S.%f")
    return f"file_validations/{ts}-{random_suffix}{ext}"


class ResultEnum(models.IntegerChoices):
    UNKNOWN = 0, ""
    PASSED = 10, "Passed"
    NOTICE = 20, "Notice"
    WARNING = 30, "Warning"
    ERROR = 40, "Error"
    CRITICAL_ERROR = 50, "Critical error"
    FATAL_ERROR = 60, "Fatal error"

    @classmethod
    def by_label(cls, label):
        for member in cls:
            if member.label == label:
                return member
        return cls.UNKNOWN


class Validation(models.Model):
    class StatusEnum(models.IntegerChoices):
        WAITING = 0
        RUNNING = 1
        SUCCESS = 2
        FAILURE = 3

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    api_key = models.ForeignKey(UserApiKey, null=True, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)

    status = models.SmallIntegerField(choices=StatusEnum)
    task_id = models.CharField(
        max_length=getattr(settings, "DJANGO_CELERY_RESULTS_TASK_ID_MAX_LENGTH", 255),
        unique=True,
        null=True,
        blank=True,
    )

    platform = models.ForeignKey(Platform, null=True, on_delete=models.SET_NULL)
    platform_name = models.CharField(max_length=150, blank=True)

    filename = models.CharField(max_length=100, blank=True)
    file = models.FileField(upload_to=validation_upload_to, null=True)
    result = models.JSONField(null=True)
    validation_result = models.PositiveSmallIntegerField(
        choices=ResultEnum,
        default=ResultEnum.UNKNOWN,
        help_text="The worst result of all the results in the validation",
    )

    memory = models.PositiveBigIntegerField(null=True)
    time = models.FloatField(null=True)

    class Meta:
        ordering = ("-id",)
        constraints = (
            models.CheckConstraint(
                condition=(models.Q(platform__isnull=True) | models.Q(platform_name="")),
                name="%(app_label)s_%(class)s_platform_union",
            ),
        )

    def __str__(self):
        if self.result:
            print(self.result.get("result"))
        return self.filename

    def save(self, *args, **kwargs):
        self.validation_result = self.extract_validation_result()
        super().save(*args, **kwargs)

    def extract_validation_result(self) -> ResultEnum:
        if self.result:
            value = self.result.get("result", ResultEnum.UNKNOWN.value)
            return ResultEnum.by_label(value)
        return ResultEnum.UNKNOWN
