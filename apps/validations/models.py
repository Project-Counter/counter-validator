import os
import string
from datetime import timedelta
from typing import IO
from urllib.parse import urlencode, urljoin
from uuid import uuid4

from core.mixins import CreatedUpdatedMixin, UUIDPkMixin
from core.models import User
from django.conf import settings
from django.db import models
from django.db.models import Case, F, Q, Value, When
from django.utils.crypto import get_random_string
from django.utils.timezone import now
from rest_framework_api_key.models import APIKey
from tailslide import Median

from validations.enums import SeverityLevel, ValidationStatus
from validations.hashing import checksum_dict, checksum_fileobj, checksum_string


# Create your models here.
def validation_upload_to(instance: "Validation", filename):
    _root, ext = os.path.splitext(filename)
    random_suffix = get_random_string(8, string.ascii_letters + string.digits)
    ts = now().strftime("%Y%m%d-%H%M%S.%f")
    return f"file_validations/{ts}-{random_suffix}{ext}"


class ValidationCoreQuerySet(models.QuerySet):
    def annotate_source(self):
        return self.annotate(
            source=Case(
                When(sushi_credentials_checksum="", then=Value("file")),
                default=Value("counter_api"),
                output_field=models.CharField(),
            )
        )

    def annotate_method(self):
        return self.annotate(
            method=Case(
                When(api_key_prefix="", then=Value("manual")),
                default=Value("api"),
                output_field=models.CharField(),
            )
        )


class ValidationCore(UUIDPkMixin, CreatedUpdatedMixin, models.Model):
    """
    This stores the core information about the validation, without the result data
    and with only the stuff that can be retained for a long time.
    All the other information is stored in Validation and "removal" of validations is done
    by deleting the Validation object - while keeping this object for long-term statistics.
    """

    MAX_ERROR_MESSAGE_LENGTH = 1000

    cop_version = models.CharField(
        max_length=16,
        blank=True,
        help_text="COUNTER CoP version as reported by the validation module",
    )
    api_endpoint = models.CharField(max_length=64, blank=True)
    report_code = models.CharField(
        max_length=16,
        blank=True,
        help_text="Code of the report as reported by the validation module",
    )
    status = models.SmallIntegerField(choices=ValidationStatus, default=ValidationStatus.WAITING)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True
    )
    user_email_checksum = models.CharField(max_length=2 * settings.HASHING_DIGEST_SIZE)
    api_key_prefix = models.CharField(max_length=8, blank=True)
    expiration_date = models.DateTimeField(null=True, blank=True)

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

    objects = ValidationCoreQuerySet.as_manager()

    class Meta:
        ordering = ["pk"]

    def __str__(self):
        return f"{self.pk}: {self.created} - {self.get_status_display()}"

    def save(self, *args, **kwargs):
        if not self.expiration_date and settings.VALIDATION_LIFETIME:
            self.expiration_date = now() + timedelta(days=settings.VALIDATION_LIFETIME)
        self.error_message = self.error_message[: self.MAX_ERROR_MESSAGE_LENGTH]
        super().save(*args, **kwargs)

    @classmethod
    def get_stats(cls, user: User | None = None) -> dict:
        """
        Get statistics of the validations.
        """
        attrs = {"total": models.Count("pk")}
        min_max_attrs = ["duration", "file_size", "used_memory"]
        for attr in min_max_attrs:
            attrs[f"{attr}__min"] = models.Min(attr)
            attrs[f"{attr}__max"] = models.Max(attr)
            attrs[f"{attr}__avg"] = models.Avg(attr)
            attrs[f"{attr}__median"] = Median(attr)

        qs = cls.objects.all()
        if user:
            qs = qs.filter(user=user)
        data = qs.aggregate(**attrs)
        # remap the keys to a nested structure
        out = {"total": data["total"]}
        for key in min_max_attrs:
            out[key] = {
                "min": data.pop(f"{key}__min"),
                "max": data.pop(f"{key}__max"),
                "avg": data.pop(f"{key}__avg"),
                "median": data.pop(f"{key}__median"),
            }
        return out

    @classmethod
    def get_time_stats(cls, user: User | None = None) -> dict:
        """
        Stats of validations by day.
        """
        result_aggregs = {
            res.name: models.Count("pk", filter=Q(validation_result=res)) for res in SeverityLevel
        }
        sl_map = {res.name: res.label for res in SeverityLevel}
        qs = cls.objects.all()
        if user:
            qs = qs.filter(user=user)
        data = (
            qs.values(date=F("created__date"))
            .annotate(total=models.Count("pk"), **result_aggregs)
            .order_by("date")
        )
        # remap severity level to labels
        out = []
        for rec in data:
            out.append(
                {
                    "date": rec["date"],
                    "total": rec["total"],
                    **{sl_map[k]: v for k, v in rec.items() if k in sl_map},
                }
            )
        return out

    @classmethod
    def get_split_stats(cls, user: User | None = None) -> dict:
        """
        Total number of validations split by the following criteria:

        * source
        * method
        * result
        """
        results = [
            When(validation_result=Value(sl.value), then=Value(sl.label)) for sl in SeverityLevel
        ]
        qs = cls.objects.all()
        if user:
            qs = qs.filter(user=user)
        data = (
            qs.annotate_source()
            .annotate_method()
            .annotate(
                result=Case(*results, default=Value("unknown")),
            )
            .values("source", "method", "result", "cop_version", "report_code")
            .annotate(count=models.Count("pk"))
        )
        return data


class ValidationQuerySet(models.QuerySet):
    def current(self):
        return self.filter(
            Q(core__expiration_date__isnull=True) | Q(core__expiration_date__gte=now())
        )

    def expired(self):
        return self.filter(core__expiration_date__lt=now())

    def public(self):
        return self.exclude(public_id__isnull=True)

    def annotate_source(self):
        return self.annotate(
            source=Case(
                When(core__sushi_credentials_checksum="", then=Value("file")),
                default=Value("counter_api"),
            )
        )

    def annotate_method(self):
        return self.annotate(
            method=Case(
                When(core__api_key_prefix="", then=Value("manual")),
                default=Value("api"),
                output_field=models.CharField(),
            )
        )


class Validation(UUIDPkMixin, models.Model):
    core = models.OneToOneField(ValidationCore, on_delete=models.CASCADE)

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
    public_id = models.UUIDField(null=True, blank=True, unique=True)

    objects = ValidationQuerySet.as_manager()

    class Meta:
        ordering = ["pk"]

    def __str__(self):
        return self.filename

    def save(self, *args, **kwargs):
        self.core.validation_result = self.extract_validation_result()
        self.core.save()
        super().save(*args, **kwargs)

    @property
    def is_counter_api_validation(self) -> bool:
        return hasattr(self, "counterapivalidation")

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
        user_note: str = "",
        api_key: APIKey | None = None,
    ) -> "Validation":
        file_checksum, file_size = checksum_fileobj(file)
        api_key_prefix = api_key.prefix if api_key else ""
        core = ValidationCore.objects.create(
            status=ValidationStatus.WAITING,
            file_size=file_size,
            file_checksum=file_checksum,
            user=user,
            user_email_checksum=checksum_string(user.email),
            api_key_prefix=api_key_prefix,
        )
        validation = cls.objects.create(
            core=core,
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

    def publish(self):
        """
        Publish the validation results.
        """
        self.public_id = uuid4()

        # Update expiration date to use public validation lifetime
        self.core.expiration_date = now() + timedelta(days=settings.PUBLIC_VALIDATION_LIFETIME)
        self.core.save(update_fields=["expiration_date"])
        self.save()

    def unpublish(self):
        """
        Unpublish the validation results.
        """
        self.public_id = None

        # Reset expiration date back to original validation lifetime
        if settings.VALIDATION_LIFETIME:
            self.core.expiration_date = now() + timedelta(days=settings.VALIDATION_LIFETIME)
        else:
            self.core.expiration_date = None
        self.core.save(update_fields=["expiration_date"])
        self.save()


class CounterAPIValidation(Validation):
    """
    This is a special validation for the COUNTER API (SUSHI).
    """

    COP_TO_URL_PREFIX = {"5.1": "r51"}

    credentials = models.JSONField(
        default=dict,
        help_text="Credentials for the SUSHI service used for the validation",
        null=True,
    )
    url = models.URLField(help_text="URL of the SUSHI service")
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
    use_short_dates = models.BooleanField(
        default=False, help_text="Use short dates (YYYY-MM instead of YYYY-MM-DD) for the request"
    )

    def save(self, *args, **kwargs):
        self.core.sushi_credentials_checksum = checksum_dict(self.credentials)
        self.core.save()
        super().save(*args, **kwargs)

    def _format_date(self, dt):
        if isinstance(dt, str):
            return dt[:7] if self.use_short_dates else dt
        return dt.strftime("%Y-%m" if self.use_short_dates else "%Y-%m-%d")

    def get_url(self):
        clean_creds = {k: v for k, v in self.credentials.items() if v} if self.credentials else {}
        if self.requested_begin_date:
            clean_creds["begin_date"] = self._format_date(self.requested_begin_date)
        if self.requested_end_date:
            clean_creds["end_date"] = self._format_date(self.requested_end_date)
        path = self.core.api_endpoint.lstrip("/")
        if path == "reports/[id]":
            path = f"reports/{self.requested_report_code.lower()}"
        # add the prefix if it's not already there
        if (
            prefix := self.COP_TO_URL_PREFIX.get(self.requested_cop_version, "")
        ) and not self.url.rstrip("/").endswith(prefix):
            path = f"{prefix}/{path}"
        # make sure arguments are sorted by key
        url = self.url if self.url.endswith("/") else f"{self.url}/"
        url = urljoin(url, path)
        if clean_creds := dict(sorted((clean_creds | self.requested_extra_attributes).items())):
            url += "?" + urlencode(clean_creds)
        return url


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
