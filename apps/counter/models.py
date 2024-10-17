from django.conf import settings
from django.db import models


# Create your models here.
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
