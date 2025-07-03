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
            },
            "reportinfo": {
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
            "datetime": "2025-03-25 09:25:14",
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
        with patch("validations.validation_module_api.async_mail_admins") as mock_mail_admins:
            validate_file(obj.pk)
            assert mock_mail_admins.call_count == 0
            assert mock.call_count == 1
            obj.refresh_from_db()
        assert obj.core.status == ValidationStatus.SUCCESS

        assert obj.core.used_memory == json["memory"]
        assert obj.core.cop_version == json["result"]["reportinfo"]["cop_version"]
        assert obj.core.report_code == json["result"]["reportinfo"]["report_id"]

    @pytest.mark.parametrize(
        ["file_name", "result", "message_count"],
        [
            ("errors.json", SeverityLevel.CRITICAL_ERROR, 8),
            ("module-error.json", SeverityLevel.FATAL_ERROR, 1),
            ("ok-result.json", SeverityLevel.PASSED, 0),
        ],
    )
    def test_task_success(self, settings, requests_mock, file_name, result, message_count):
        file = SimpleUploadedFile(file_name, b"test data")
        obj = Validation.create_from_file(user=UserFactory(), file=file)
        obj.core.status = ValidationStatus.WAITING
        obj.core.save()
        with open(settings.BASE_DIR / "test_data/validation_results/" / file_name) as datafile:
            mock = requests_mock.post(re.compile(".*"), text=datafile.read(), status_code=200)
            validate_file(obj.pk)
            assert mock.called_once
        obj.refresh_from_db()
        assert obj.core.status == ValidationStatus.SUCCESS
        assert obj.core.validation_result == result
        assert obj.messages.count() == message_count, (
            f"There are {message_count} messages in the test file"
        )

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

    def test_task_result_save_error(self, requests_mock):
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
        obj.refresh_from_db()
        assert obj.core.status == ValidationStatus.FAILURE
        assert obj.core.error_message == "test"

    def test_task_reportinfo_data_copied_to_header(self, settings, requests_mock):
        """
        Test that data from the reportinfo attribute is properly stored in
        result_data['reportinfo'].
        """
        file = SimpleUploadedFile("ok-result.json", b"test data")
        obj = Validation.create_from_file(user=UserFactory(), file=file)
        obj.core.status = ValidationStatus.WAITING
        obj.core.save()

        with open(settings.BASE_DIR / "test_data/validation_results/ok-result.json") as datafile:
            mock = requests_mock.post(re.compile(".*"), text=datafile.read(), status_code=200)
            validate_file(obj.pk)
            assert mock.called_once

        obj.refresh_from_db()
        assert obj.core.status == ValidationStatus.SUCCESS
        assert obj.core.validation_result == SeverityLevel.PASSED

        # Verify that the header data is stored in result_data
        assert obj.result_data is not None
        assert "header" in obj.result_data
        header = obj.result_data["header"]

        # Check that the header contains the expected report data
        assert "report" in header
        report = header["report"]
        assert report["A1"] == "Report_Name"
        assert report["B1"] == "Title Master Report"
        assert report["A2"] == "Report_ID"
        assert report["B2"] == "TR"
        assert report["A3"] == "Release"
        assert report["B3"] == "5"
        assert report["A4"] == "Institution_Name"
        assert report["B4"] == "Client Demo Site"
        assert report["A5"] == "Institution_ID"
        assert report["B5"] == "ISNI:1234123412341234"
        assert report["A11"] == "Created"
        assert report["B11"] == "2019-04-25T11:39:56Z"
        assert report["A12"] == "Created_By"
        assert report["B12"] == "Publisher Platform Delta"
        assert report["A10"] == "Reporting_Period"
        assert report["B10"] == "Begin_Date=2016-01-01; End_Date=2016-03-31"

        # Check that the header contains the expected result data
        assert "result" in header
        result = header["result"]
        assert len(result) == 7
        assert result[0] == "Validation Result for COUNTER Release 5 Report"
        assert result[2] == "Title Master Report (TR)"
        assert result[3] == "for Client Demo Site"
        assert result[4] == "created 2019-04-25T11:39:56Z by Publisher Platform Delta"
        assert result[5] == "covering 2016-01-01 to 2016-03-31"

        # Check that reportinfo data is stored in result_data['reportinfo']
        assert "reportinfo" in obj.result_data
        reportinfo = obj.result_data["reportinfo"]
        assert reportinfo["report_id"] == "TR"
        assert reportinfo["format"] == "tabular"
        assert reportinfo["cop_version"] == "5"
        assert reportinfo["institution_name"] == "Client Demo Site"
        assert reportinfo["created"] == "2019-04-25T11:39:56Z"
        assert reportinfo["created_by"] == "Publisher Platform Delta"
        assert reportinfo["begin_date"] == "2016-01-01"
        assert reportinfo["end_date"] == "2016-03-31"

    def test_task_error_in_update_validation_result(self, requests_mock):
        """
        Test that when the task crashed during save of the model, the status will
        be FAILED and not RUNNING
        """
        file = SimpleUploadedFile("tr.csv", b"test data")
        obj = Validation.create_from_file(user=UserFactory(), file=file)
        obj.core.status = ValidationStatus.WAITING
        obj.core.save()
        json = ResponseMock.json()
        requests_mock = requests_mock.post(re.compile(".*"), json=json, status_code=200)
        with patch("validations.tasks.update_validation_result") as mock:
            mock.side_effect = Exception("test")
            validate_file(obj.pk)
            assert mock.call_count == 1
        obj.refresh_from_db()
        assert obj.core.status == ValidationStatus.FAILURE
        assert obj.core.error_message == "test"


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
        assert obj.core.cop_version == json["result"]["reportinfo"]["cop_version"]
        assert obj.core.report_code == json["result"]["reportinfo"]["report_id"]
        assert obj.file is not None
        assert obj.core.file_size > 0
        with open("test_data/reports/50-Sample-TR.json", "rb") as infile:
            assert obj.file.read() == infile.read()
        assert obj.filename.startswith("COUNTER API")

    def test_task_error_in_update_validation_result(self, requests_mock):
        obj = CounterAPIValidationFactory(
            core__user=UserFactory(), core__status=ValidationStatus.WAITING
        )
        json = ResponseMock.json()
        requests_mock = requests_mock.post(re.compile(".*"), json=json, status_code=200)
        with patch("validations.tasks.update_validation_result") as mock:
            mock.side_effect = Exception("test")
            validate_counter_api(obj.pk)
            assert mock.call_count == 1
        obj.refresh_from_db()
        assert obj.core.status == ValidationStatus.FAILURE
        assert obj.core.error_message == "test"

    @pytest.mark.parametrize(
        "url", ["https://foo.bar/", "https://foo.bar/sushi/", "https://foo.bar/a/b/c/d"]
    )
    def test_different_urls(self, requests_mock, url):
        obj = CounterAPIValidationFactory(
            url=url, core__user=UserFactory(), core__status=ValidationStatus.WAITING
        )
        mock = requests_mock.post("http://localhost:8180/sushi.php", json={})
        validate_counter_api(obj.pk)
        assert mock.called_once
        sent_url = mock.last_request.json()["url"]
        assert sent_url.startswith(url)
