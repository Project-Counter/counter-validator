import os
import string

from core.models import UserApiKey
from counter.models import Platform
from django.conf import settings
from django.db import models
from django.utils.crypto import get_random_string
from django.utils.timezone import now


# Create your models here.
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

    filename = models.CharField(max_length=100, blank=True, help_text="Original filename")
    file = models.FileField(upload_to=validation_upload_to, null=True)
    result_data = models.JSONField(null=True)
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
        if self.result_data:
            print(self.result_data.get("result"))
        return self.filename

    def save(self, *args, **kwargs):
        self.validation_result = self.extract_validation_result()
        super().save(*args, **kwargs)

    def extract_validation_result(self) -> ResultEnum:
        if self.result_data:
            value = self.result_data.get("result", ResultEnum.UNKNOWN.value)
            return ResultEnum.by_label(value)
        return ResultEnum.UNKNOWN
