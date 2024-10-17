"""
Platform, report and SUSHI service synchronisation tests (with the COUNTER Registry).
"""

import json
from pathlib import Path

import pytest

from core.classes.registry import RegistrySync
from core.models import Platform, Report, ReportToPlatform, SushiService
from core.serializers import PlatformSerializer, SushiServiceSerializer
from core.tasks import update_registry_models

folder = Path(__file__).resolve().parent


class RegistrySyncMock(RegistrySync):
    def __init__(self, platform_file):
        self.platform_file = platform_file
        self.platform_data = None
        self.sushi_data = {}

    def get_platforms(self):
        if not self.platform_data:
            with open(folder / "test_data" / self.platform_file) as fp:
                self.platform_data = json.load(fp)
        return self.platform_data

    def get_sushi(self, url):
        uuid = url.split("/")[-2]
        if uuid not in self.sushi_data:
            path = folder / "test_data" / "sushi_service" / (uuid + ".json")
            with open(path) as fp:
                self.sushi_data[uuid] = json.load(fp)
        return self.sushi_data[uuid]

    def check(self):
        fields = set(PlatformSerializer.Meta.fields) - {
            "id",
            "deprecated",
            "reports",
            "sushi_services",
        }
        for d in self.platform_data:
            platform = Platform.objects.get(id=d["id"])
            for f in fields:
                assert getattr(platform, f) == d[f]
            for r in d["reports"]:
                r.pop("report_name")
                report = Report.objects.get(**r)
                ReportToPlatform.objects.get(report=report, platform=platform)
            for s in d["sushi_services"]:
                SushiService.objects.get(platform=platform, id=s["url"].split("/")[-2])
        fields = set(SushiServiceSerializer.Meta.fields) - {"id", "deprecated"}
        for k, v in self.sushi_data.items():
            service = SushiService.objects.get(id=k)
            for f in fields:
                assert getattr(service, f) == v[f]


@pytest.mark.django_db
class TestRegistry:
    def test_task(self):
        mock = RegistrySyncMock("platform1.json")
        update_registry_models(mock)
        mock.check()

        mock = RegistrySyncMock("platform2.json")
        update_registry_models(mock)
        mock.check()

        p = Platform.objects.get(id="bf9a2458-2386-48c5-a810-4a33c2dacf80")
        r = Report.objects.get(report_id="TR")
        assert (
            ReportToPlatform.objects.filter(platform=p, report=r).count() == 0
        ), "removed reports should be unlinked"

        assert (
            Platform.objects.filter(
                id="60d34416-9666-4b09-8d58-220ffc04901e", deprecated=True
            ).count()
            == 1
        ), "removed platforms should be deprecated"
        assert (
            SushiService.objects.filter(
                id="21f2d1ed-76fe-4ecc-b939-83209f3de125", deprecated=True
            ).count()
            == 1
        ), "removed sushi services should be deprecated"
