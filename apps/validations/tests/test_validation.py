"""
File and SUSHI validation tests.
"""

import re
from unittest.mock import patch
from uuid import UUID

import pytest
import requests_mock
from core.fake_data import UserFactory
from core.tasks import validate_file
from counter.fake_data import PlatformFactory
from django.conf import settings as django_settings
from django.core.files import File
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse

from validations.enums import SeverityLevel, ValidationStatus
from validations.models import Validation


class ResponseMock:
    @staticmethod
    def raise_for_status():
        pass

    @staticmethod
    def json():
        return {
            "result": {
                "result": "Warning",
                "messages": [
                    {
                        "data": "",
                        "level": 2,
                        "header": "Row 1",
                        "number": 1,
                        "message": "some warning",
                    },
                ],
            },
            "memory": 4194304,
        }


def post_mock(pk, status):
    def mock(*args, **kwargs):
        assert Validation.objects.filter(pk=pk, core__status=status).count() == 1

        assert args[0] == django_settings.CTOOLS_URL + "file.php"
        assert kwargs["params"]["extension"] == "csv"
        assert isinstance(kwargs["data"], File)

        return ResponseMock()

    return mock


@pytest.mark.django_db
class TestValidationAPI:
    def test_api_okay(self, client_authenticated_user):
        filename = "tr.json"
        file = SimpleUploadedFile(filename, content=b"xxx")
        with patch("core.tasks.validate_file.delay_on_commit") as p:
            res = client_authenticated_user.post(
                reverse("validation-file"),
                data={"file": file, "platform_name": "test"},
                format="multipart",
            )
            p.assert_called_once_with(UUID(res.json()["id"]))
        assert res.status_code == 201
        assert res.json()["filename"] == filename
        val = Validation.objects.select_related("core").get()
        assert val.filename == filename
        assert val.core.platform_name == "test"
        assert str(val.pk) == res.json()["id"]

    def test_api_empty(self, client_authenticated_user):
        file = SimpleUploadedFile("tr.json", content=b"")
        with patch("core.tasks.validate_file.delay_on_commit") as p:
            res = client_authenticated_user.post(
                reverse("validation-file"),
                data={"file": file},
                format="multipart",
            )
            p.assert_not_called()
        assert res.status_code == 400
        assert "empty" in res.json()["file"][0]

    def test_api_large(self, settings, client_authenticated_user):
        settings.MAX_FILE_SIZE = 1023
        file = SimpleUploadedFile("tr.json", content=b"X" * (settings.MAX_FILE_SIZE + 1))
        with patch("core.tasks.validate_file.delay_on_commit") as p:
            res = client_authenticated_user.post(
                reverse("validation-file"),
                data={"file": file},
                format="multipart",
            )
            p.assert_not_called()
        assert res.status_code == 400
        assert "Max file size exceeded" in res.json()["file"][0]

    @pytest.mark.parametrize(
        ["platform_name", "platform_id", "exp_name"],
        [
            ("test", None, "test"),
            ("test", "12345678-1234-5678-1234-567812345678", "FooBar"),
            ("", "12345678-1234-5678-1234-567812345678", "FooBar"),
            ("", None, ""),
        ],
    )
    def test_platform_name_and_id(
        self, client_authenticated_user, platform_name, platform_id, exp_name
    ):
        """
        Test different combinations of platform_name and platform_id to make sure that the
        platform_name is set correctly:

        * if only platform_name is set, it should be used
        * if both are set, platform_name should be taken from the platform object
        * if only platform_id is set, platform_name should also be taken from the platform object
        """
        # create a platform object - it is there for every version of the test
        PlatformFactory(id="12345678-1234-5678-1234-567812345678", name="FooBar")
        file = SimpleUploadedFile("tr.json", content=b"xxx")
        pl_data = {"platform_name": platform_name}
        if platform_id:
            pl_data["platform"] = platform_id
        with patch("core.tasks.validate_file.delay_on_commit") as p:
            res = client_authenticated_user.post(
                reverse("validation-file"),
                data={"file": file, **pl_data},
                format="multipart",
            )
            p.assert_called_once_with(UUID(res.json()["id"]))
        assert res.status_code == 201
        val = Validation.objects.select_related("core").get()
        assert val.core.platform_name == exp_name
        if platform_id:
            assert str(val.core.platform_id) == platform_id
        else:
            assert val.core.platform_id is None


@pytest.mark.django_db
class TestValidationTask:
    def test_task_simple(self):
        file = SimpleUploadedFile("tr.csv", b"test data")
        obj = Validation.create_from_file(user=UserFactory(), file=file)
        insert_assert = post_mock(obj.pk, ValidationStatus.RUNNING)
        with patch("requests.post", wraps=insert_assert) as p:
            validate_file(obj.pk)
            p.assert_called_once()
        obj.refresh_from_db()
        assert obj.core.status == ValidationStatus.SUCCESS
        json = ResponseMock.json()
        assert "messages" in json["result"]
        assert obj.core.used_memory == json["memory"]

    def test_task_test1(self, settings):
        file = SimpleUploadedFile("test1.json", b"test data")
        obj = Validation.create_from_file(user=UserFactory(), file=file)
        obj.core.status = ValidationStatus.WAITING
        obj.core.save()
        with requests_mock.Mocker() as m:
            with open(settings.BASE_DIR / "test_data/validation_results/test1.json") as datafile:
                m.post(
                    re.compile(".*"),
                    text=datafile.read(),
                    status_code=200,
                )
            validate_file(obj.pk)
            assert m.called_once
        obj.refresh_from_db()
        assert obj.core.status == ValidationStatus.SUCCESS
        assert obj.core.validation_result == SeverityLevel.WARNING
