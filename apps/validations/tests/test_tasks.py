"""
File and SUSHI validation tests.
"""

import re
from unittest.mock import patch

import pytest
import requests_mock
from core.fake_data import UserFactory
from django.conf import settings as django_settings
from django.core.files import File
from django.core.files.uploadedfile import SimpleUploadedFile

from validations.enums import SeverityLevel, ValidationStatus
from validations.models import Validation
from validations.tasks import validate_file


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

    def test_task_success(self, settings):
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

    @pytest.mark.parametrize("http_status", [400, 401, 403, 404, 405, 500])
    def test_task_c5tools_error(self, http_status):
        file = SimpleUploadedFile("tr.csv", b"test data")
        obj = Validation.create_from_file(user=UserFactory(), file=file)
        with requests_mock.Mocker() as m:
            m.post(
                re.compile(".*"),
                text="error",
                status_code=http_status,
            )
            validate_file(obj.pk)
            assert m.called_once
        obj.refresh_from_db()
        assert obj.core.status == ValidationStatus.FAILURE
        assert obj.core.validation_result == SeverityLevel.UNKNOWN
        assert obj.core.used_memory == 0
        assert obj.core.stats == {}
        assert obj.core.duration > 0
        assert obj.core.error_message != ""
