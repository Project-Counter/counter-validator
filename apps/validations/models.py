import os
import string
from typing import IO
from urllib.parse import urlencode, urljoin

from core.mixins import CreatedUpdatedMixin, UUIDPkMixin
from core.models import User
from counter.models import Platform
from django.conf import settings
from django.db import models
from django.utils.crypto import get_random_string
from django.utils.timezone import now
from rest_framework_api_key.models import APIKey

from validations.enums import SeverityLevel, ValidationStatus
from validations.hashing import checksum_dict, checksum_fileobj, checksum_string


# Create your models here.
def validation_upload_to(instance: "Validation", filename):
    _root, ext = os.path.splitext(filename)
    random_suffix = get_random_string(8, string.ascii_letters + string.digits)
    ts = now().strftime("%Y%m%d-%H%M%S.%f")
    return f"file_validations/{ts}-{random_suffix}{ext}"


class ValidationCore(UUIDPkMixin, CreatedUpdatedMixin, models.Model):
    """
    This stores the core information about the validation, without the result data
    and with only the stuff that can be retained for a long time.
    All the other information is stored in Validation and "removal" of validations is done
    by deleting the Validation object - while keeping this object for long-term statistics.
    """

    cop_version = models.CharField(
        max_length=16,
        blank=True,
        help_text="COUNTER CoP version as reported by the validation module",
    )
    report_code = models.CharField(
        max_length=16,
        blank=True,
        help_text="Code of the report as reported by the validation module",
    )
    status = models.SmallIntegerField(choices=ValidationStatus, default=ValidationStatus.WAITING)
    user_email_checksum = models.CharField(max_length=2 * settings.HASHING_DIGEST_SIZE)
    api_key_prefix = models.CharField(max_length=8, blank=True)

    platform = models.ForeignKey(
        Platform,
        null=True,
        on_delete=models.SET_NULL,
        help_text="If the platform is in the registry, this can link it",
    )
    platform_name = models.CharField(
        max_length=150,
        blank=True,
        help_text="Contains the platform name supplied by the user. If `platform` is set, "
        "this is a copy of the platform name",
    )

    validation_result = models.PositiveSmallIntegerField(
        choices=SeverityLevel,
        default=SeverityLevel.UNKNOWN,
        help_text="The worst result of all the results in the validation",
    )

    file_checksum = models.CharField(max_length=2 * settings.HASHING_DIGEST_SIZE, blank=True)
    file_size = models.PositiveBigIntegerField(
        help_text="Size of the validated file in bytes", default=0
    )
    used_memory = models.PositiveBigIntegerField(
        help_text="Memory in bytes used by the validation module", default=0
    )
    duration = models.FloatField(
        default=0, help_text="Time in seconds used by the validation module"
    )
    stats = models.JSONField(
        default=dict,
        blank=True,
        help_text="Statistics from the validation module - number of messages for each severity",
    )
    sushi_credentials_checksum = models.CharField(
        max_length=2 * settings.HASHING_DIGEST_SIZE, blank=True
    )
    error_message = models.TextField(blank=True)

    class Meta:
        ordering = ["pk"]

    def __str__(self):
        return f"{self.pk}: {self.created} - {self.get_status_display()}"


class Validation(UUIDPkMixin, models.Model):
    core = models.OneToOneField(ValidationCore, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    task_id = models.CharField(
        max_length=getattr(settings, "DJANGO_CELERY_RESULTS_TASK_ID_MAX_LENGTH", 255),
        unique=True,
        null=True,
        blank=True,
    )

    filename = models.CharField(max_length=256, blank=True, help_text="Original filename")
    file = models.FileField(upload_to=validation_upload_to, null=True)
    result_data = models.JSONField(null=True)
    user_note = models.TextField(blank=True)

    class Meta:
        ordering = ["pk"]

    def __str__(self):
        return self.filename

    def save(self, *args, **kwargs):
        self.core.validation_result = self.extract_validation_result()
        self.core.save()
        super().save(*args, **kwargs)

    def extract_validation_result(self) -> SeverityLevel:
        if self.result_data:
            value = self.result_data.get("result", SeverityLevel.UNKNOWN.value)
            return SeverityLevel.by_label(value)
        return SeverityLevel.UNKNOWN

    @classmethod
    def create_from_file(
        cls,
        user: User,
        file: IO,
        platform: Platform | None = None,
        platform_name: str = "",
        user_note: str = "",
        api_key: APIKey | None = None,
    ) -> "Validation":
        file_checksum, file_size = checksum_fileobj(file)
        api_key_prefix = api_key.prefix if api_key else ""
        core = ValidationCore.objects.create(
            status=ValidationStatus.WAITING,
            platform=platform,
            platform_name=platform_name,
            file_size=file_size,
            file_checksum=file_checksum,
            user_email_checksum=checksum_string(user.email),
            api_key_prefix=api_key_prefix,
        )
        validation = cls.objects.create(
            core=core,
            user=user,
            filename=file.name,
            file=file,
            user_note=user_note,
        )
        return validation

    def file_url(self):
        if self.file:
            return self.file.url
        return None

    def add_result(self, result: dict) -> dict:
        """
        Add JSON to the `result_data` field after extracting the messages into separate objects.
        It returns a statistics of message levels.
        """
        messages = result.pop("messages", [])
        m_to_store = []
        stats = {}
        for i, message in enumerate(messages, 1):
            m = ValidationMessage.from_dict(self, i, message)
            m_to_store.append(m)
            stats[m.get_severity_display()] = stats.get(m.get_severity_display(), 0) + 1

        ValidationMessage.objects.bulk_create(m_to_store)
        self.result_data = result
        return stats

    def get_summary_stats(self):
        """
        Statistics of messages with specific summary.
        """
        return {
            rec["summary"]: rec["count"]
            for rec in ValidationMessage.objects.filter(validation=self)
            .values("summary")
            .annotate(count=models.Count("summary"))
            .order_by("-count")
        }

    def get_summary_severity_stats(self):
        """
        Statistics of messages with specific severity.
        """
        out = (
            ValidationMessage.objects.filter(validation=self)
            .values("summary", "severity")
            .annotate(count=models.Count("severity"))
            .order_by("-severity", "-count")
        )
        for rec in out:
            rec["severity"] = SeverityLevel(rec["severity"]).label
        return out


class CounterAPIValidation(Validation):
    """
    This is a special validation for the Counter API (SUSHI).
    """

    COP_TO_URL_PREFIX = {"5.1": "/r51"}

    credentials = models.JSONField(
        default=dict, help_text="Credentials for the SUSHI service used for the validation"
    )
    url = models.URLField(help_text="URL of the SUSHI service")
    api_endpoint = models.CharField(default="reports", max_length=64)
    requested_cop_version = models.CharField(
        max_length=16,
        blank=True,
        help_text="COUNTER CoP version requested from the server",
    )
    requested_report_code = models.CharField(
        max_length=16,
        blank=True,
        help_text="Report code requested from the server",
    )
    requested_extra_attributes = models.JSONField(
        default=dict,
        blank=True,
        help_text="Extra attributes for the SUSHI request, e.g. report filters",
    )
    # dates are not required for all endpoints
    requested_begin_date = models.DateField(null=True, blank=True)
    requested_end_date = models.DateField(null=True, blank=True)

    def save(self, *args, **kwargs):
        self.core.sushi_credentials_checksum = checksum_dict(self.credentials)
        self.core.save()
        super().save(*args, **kwargs)

    def get_url(self):
        clean_creds = {k: v for k, v in self.credentials.items() if v}
        return (
            urljoin(
                self.url,
                f"{self.COP_TO_URL_PREFIX.get(self.requested_cop_version, '')}"
                f"/reports/{self.requested_report_code.lower()}",
            )
            + "?"
            + urlencode(
                clean_creds
                | {
                    "begin_date": self.requested_begin_date,
                    "end_date": self.requested_end_date,
                    **self.requested_extra_attributes,
                }
            )
        )


class ValidationMessage(UUIDPkMixin, models.Model):
    KEY_TO_ATTR = {
        "d": "data",
        "l": {"attr": "severity", "converter": SeverityLevel.by_label},
        "h": "hint",
        "m": "message",
        "p": "location",
        "s": "summary",
    }

    validation = models.ForeignKey(Validation, on_delete=models.CASCADE, related_name="messages")
    number = models.PositiveIntegerField(
        default=0, help_text="Order of the message inside the validation results"
    )
    severity = models.PositiveSmallIntegerField(choices=SeverityLevel)
    code = models.CharField(max_length=16, blank=True)
    location = models.TextField(blank=True)
    message = models.TextField()
    summary = models.TextField()
    hint = models.TextField(blank=True)
    data = models.TextField(blank=True)

    class Meta:
        ordering = ["validation", "number", "pk"]
        unique_together = ("validation", "number")

    def __str__(self):
        return f"{self.get_level_display()}: {self.message}"

    @classmethod
    def from_dict(cls, validation: Validation, number: int, data: dict) -> "ValidationMessage":
        kwargs = {}
        for key, attr in cls.KEY_TO_ATTR.items():
            value = data.get(key)
            if isinstance(attr, dict):
                if converter := attr.get("converter"):
                    value = converter(value)
                attr = attr["attr"]
            kwargs[attr] = value or ""  # None is not allowed
        return cls(validation=validation, number=number, **kwargs)
