"""
File and SUSHI validation tests.
"""
import re
from pathlib import Path
from typing import Optional
from unittest.mock import patch

import pytest
import requests_mock
from django.conf import settings
from django.core.files import File
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse

from core.models import Validation, ResultEnum
from core.tasks import validate_file
from core.tests.fake_data import UserFactory


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
        assert Validation.objects.filter(pk=pk, status=status).count() == 1

        assert args[0] == settings.CTOOLS_URL + "file.php"
        assert kwargs["params"]["extension"] == "csv"
        assert isinstance(kwargs["data"], File)

        return ResponseMock()

    return mock


@pytest.mark.django_db
class TestValidationAPI:
    def test_api_okay(self, client_authenticated_user):
        filename = "tr.json"
        with patch("core.tasks.validate_file.delay_on_commit") as p:
            res = client_authenticated_user.post(
                reverse("validation-file", kwargs={"filename": filename}),
                data="xxx",
                content_type="application/octet-stream",
            )
            p.assert_called_once_with(res.json()["id"])
        assert res.status_code == 201
        assert res.json()["filename"] == filename
        assert Validation.objects.filter(id=res.json()["id"], filename=filename).count() == 1

    def test_api_empty(self, client_authenticated_user):
        filename = "tr.json"
        with patch("core.tasks.validate_file.delay_on_commit") as p:
            res = client_authenticated_user.post(
                reverse("validation-file", kwargs={"filename": filename}),
                data="",
                content_type="application/octet-stream",
            )
            p.assert_not_called()
        assert res.status_code == 400
        assert "Empty files" in res.json()[0]

    def test_api_large(self, settings, client_authenticated_user):
        settings.MAX_FILE_SIZE = 1023
        filename = "tr.json"
        with patch("core.tasks.validate_file.delay_on_commit") as p:
            res = client_authenticated_user.post(
                reverse("validation-file", kwargs={"filename": filename}),
                data="X" * (settings.MAX_FILE_SIZE + 1),
                content_type="application/octet-stream",
            )
            p.assert_not_called()
        assert res.status_code == 400
        assert "Max file size exceeded" in res.json()[0]


@pytest.mark.django_db
class TestValidationTask:
    def test_task_simple(self):
        file = SimpleUploadedFile("tr.csv", b"test data")
        obj = Validation.objects.create(
            user=UserFactory(),
            status=Validation.StatusEnum.WAITING,
            filename=file.name,
            file=file,
        )
        insert_assert = post_mock(obj.pk, Validation.StatusEnum.RUNNING)
        with patch("requests.post", wraps=insert_assert) as p:
            validate_file(obj.pk)
            p.assert_called_once()
        obj.refresh_from_db()
        assert obj.status == Validation.StatusEnum.SUCCESS
        json = ResponseMock.json()
        assert "messages" in json["result"]
        assert obj.memory == json["memory"]

    def test_task_test1(self):
        file = SimpleUploadedFile("test1.json", b"test data")
        obj = Validation.objects.create(
            user=UserFactory(),
            status=Validation.StatusEnum.WAITING,
            filename=file.name,
            file=file,
        )
        with requests_mock.Mocker() as m:
            with open(Path(__file__).parent / "test_data/validation_results/test1.json") as datafile:
                m.post(
                    re.compile(".*"),
                    text=datafile.read(),
                    status_code=200,
                )
            validate_file(obj.pk)
            assert m.called_once
        obj.refresh_from_db()
        assert obj.status == Validation.StatusEnum.SUCCESS
        assert obj.validation_result == ResultEnum.WARNING
