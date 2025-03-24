"""
File and SUSHI validation tests.
"""

import re
from base64 import b64encode
from unittest.mock import patch
from zlib import compress

import pytest
from core.fake_data import UserFactory
from django.core.files.uploadedfile import SimpleUploadedFile

from validations.enums import SeverityLevel, ValidationStatus
from validations.fake_data import CounterAPIValidationFactory
from validations.models import Validation
from validations.tasks import validate_counter_api, validate_file


class ResponseMock:
    data = {
        "result": {
            "result": "Warning",
            "header": {
                "report": {"A1": "Foobar"},
                "result": ["This is a report", 'for "Foobar"'],
                "cop_version": "5",
                "report_id": "TR",
                "created": "2021-09-30T14:00:00",
                "institution_name": "FooBar",
                "created_by": "XYZ",
                "begin_date": "2024-09-01",
                "end_date": "2024-09-30",
            },
            "messages": [
                {
                    "d": ":)",
                    "l": "Warning",
                    "h": "You should do something about it",
                    "p": "element.Report_Header",
                    "m": "Report header is messed up :)",
                    "s": "Report header is messed up",
                },
            ],
        },
        "memory": 4194304,
    }

    @staticmethod
    def raise_for_status():
        pass

    @classmethod
    def json(cls):
        return cls.data


class ResponseMockCounterAPI(ResponseMock):
    @classmethod
    def json(cls):
        out = super().json()
        with open("test_data/reports/50-Sample-TR.json", "rb") as infile:
            out["report"] = b64encode(compress(infile.read(), 3)).decode()
        return out


@pytest.mark.django_db
class TestFileValidationTask:
    def test_task_simple(self, requests_mock):
        file = SimpleUploadedFile("tr.csv", b"test data")
        obj = Validation.create_from_file(user=UserFactory(), file=file)
        json = ResponseMock.json()
        mock = requests_mock.post(re.compile(".*"), json=json, status_code=200)
        validate_file(obj.pk)
        assert mock.called_once
        obj.refresh_from_db()
        assert obj.core.status == ValidationStatus.SUCCESS

        assert obj.core.used_memory == json["memory"]
        assert obj.core.cop_version == json["result"]["header"]["cop_version"]
        assert obj.core.report_code == json["result"]["header"]["report_id"]

    def test_task_success(self, settings, requests_mock):
        file = SimpleUploadedFile("test1.json", b"test data")
        obj = Validation.create_from_file(user=UserFactory(), file=file)
        obj.core.status = ValidationStatus.WAITING
        obj.core.save()
        with open(settings.BASE_DIR / "test_data/validation_results/test1.json") as datafile:
            mock = requests_mock.post(re.compile(".*"), text=datafile.read(), status_code=200)
            validate_file(obj.pk)
            assert mock.called_once
        obj.refresh_from_db()
        assert obj.core.status == ValidationStatus.SUCCESS
        assert obj.core.validation_result == SeverityLevel.WARNING
        assert "messages" not in obj.result_data
        assert "Warning" in obj.core.stats
        assert obj.messages.count() == 165, "There are 165 messages in the test file"

    @pytest.mark.parametrize("http_status", [400, 401, 403, 404, 405, 500])
    def test_task_c5tools_error(self, http_status, requests_mock):
        file = SimpleUploadedFile("tr.csv", b"test data")
        obj = Validation.create_from_file(user=UserFactory(), file=file)
        mock = requests_mock.post(re.compile(".*"), text="error", status_code=http_status)
        validate_file(obj.pk)
        assert mock.called_once
        obj.refresh_from_db()
        assert obj.core.status == ValidationStatus.FAILURE
        assert obj.core.validation_result == SeverityLevel.UNKNOWN
        assert obj.core.used_memory == 0
        assert obj.core.stats == {}
        assert obj.core.duration > 0
        assert obj.core.error_message != ""

    def test_task_result_save_error(self, settings, requests_mock):
        """
        Test that when the task crashed during save of the model, the status will
        be FAILED and not RUNNING
        """
        file = SimpleUploadedFile("tr.csv", b"test data")
        obj = Validation.create_from_file(user=UserFactory(), file=file)
        obj.core.status = ValidationStatus.WAITING
        obj.core.save()
        with patch("validations.tasks.requests.post") as mock:
            # raise exception when json is called which should break the task
            # after the request status is checked
            mock.return_value.json.side_effect = Exception("test")
            validate_file(obj.pk)
            assert mock.call_count == 1
            assert mock.return_value.raise_for_status.call_count == 1
            assert mock.return_value.json.call_count == 1
        obj.refresh_from_db()
        assert obj.core.status == ValidationStatus.FAILURE


@pytest.mark.django_db
class TestCounterAPIValidationTask:
    def test_task_simple(self, requests_mock):
        obj = CounterAPIValidationFactory(
            core__user=UserFactory(), core__status=ValidationStatus.WAITING
        )
        json = ResponseMockCounterAPI.json()
        mock = requests_mock.post(re.compile(".*"), json=json, status_code=200)
        validate_counter_api(obj.pk)
        assert mock.called_once
        obj.refresh_from_db()
        assert obj.core.status == ValidationStatus.SUCCESS
        assert obj.core.used_memory == json["memory"]
        assert obj.core.cop_version == json["result"]["header"]["cop_version"]
        assert obj.core.report_code == json["result"]["header"]["report_id"]
        assert obj.file is not None
        with open("test_data/reports/50-Sample-TR.json", "rb") as infile:
            assert obj.file.read() == infile.read()
        assert obj.filename.startswith("Counter API")
