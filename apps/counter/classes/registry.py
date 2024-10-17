import logging

import requests
from django.conf import settings
from django.db import models

from counter.models import Platform, Report, SushiService
from counter.serializers import PlatformSerializer, ReportSerializer, SushiServiceSerializer

logger = logging.getLogger(__name__)


def get_or_none(model_class: type[models.Model], *args, **kwargs):
    try:
        return model_class.objects.get(*args, **kwargs)
    except model_class.DoesNotExist:
        return None


class RegistrySync:
    def __init__(self):
        self.client = requests.Session()
        self.base_url = f"{settings.REGISTRY_URL}/api/v1/"

    def get_platforms(self):
        url = f"{self.base_url}/platform/"
        resp = self.client.get(url)
        if resp.status_code != 200:
            raise RuntimeError(f"{url} returned non OK status code ({resp.status_code})")
        return resp.json()

    def get_sushi(self, url):
        resp = self.client.get(url)
        if resp.status_code != 200:
            raise RuntimeError(f"Failed to download sushi service {url}")
        return resp.json()

    def sync(self):
        seen_platform_ids = set()
        seen_sushi_service_ids = set()

        logger.debug("Getting platform list")
        platforms = self.get_platforms()
        for i, platform_data in enumerate(platforms):
            logger.debug("Processing platform %d/%d", i + 1, len(platforms))
            serializer = PlatformSerializer(
                get_or_none(Platform, pk=platform_data["id"]), data=platform_data
            )
            serializer.is_valid(raise_exception=True)
            platform = serializer.save()
            seen_platform_ids.add(platform.id)

            # fill in and update report types
            reports = []
            for report_data in platform_data.get("reports", []):
                rep_serializer = ReportSerializer(
                    get_or_none(Report, pk=report_data["report_id"]),
                    data=report_data,
                )
                rep_serializer.is_valid(raise_exception=True)
                report = rep_serializer.save()
                reports.append(report)

            platform.reports.set(reports)

            # fill in and update sushi services
            sushi_services = []
            for sushi_service_link in platform_data.get("sushi_services", []):
                service_data = self.get_sushi(sushi_service_link["url"])
                ser_serializer = SushiServiceSerializer(
                    get_or_none(SushiService, pk=service_data["id"]),
                    data=service_data,
                )
                ser_serializer.is_valid(raise_exception=True)
                sushi_service = ser_serializer.save()
                seen_sushi_service_ids.add(sushi_service.id)
                sushi_services.append(sushi_service)
            platform.sushi_services.set(sushi_services)

        # mark removed
        Platform.objects.filter(id__in=seen_platform_ids).update(deprecated=False)
        Platform.objects.exclude(id__in=seen_platform_ids).update(deprecated=True)
        SushiService.objects.filter(id__in=seen_sushi_service_ids).update(deprecated=False)
        SushiService.objects.exclude(id__in=seen_sushi_service_ids).update(deprecated=True)
