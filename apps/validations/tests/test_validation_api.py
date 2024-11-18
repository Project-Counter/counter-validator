from unittest.mock import patch
from uuid import UUID

import factory
import pytest
from counter.fake_data import PlatformFactory
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse

from validations.fake_data import CounterAPIValidationRequestDataFactory, ValidationFactory
from validations.models import Validation, ValidationCore


@pytest.mark.django_db
class TestFileValidationAPI:
    def test_api_okay(self, client_authenticated_user):
        filename = "tr.json"
        file = SimpleUploadedFile(filename, content=b"xxx")
        with patch("validations.tasks.validate_file.delay_on_commit") as p:
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
        with patch("validations.tasks.validate_file.delay_on_commit") as p:
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
        with patch("validations.tasks.validate_file.delay_on_commit") as p:
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
        with patch("validations.tasks.validate_file.delay_on_commit") as p:
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

    def test_validation_list(
        self, client_authenticated_user, normal_user, django_assert_max_num_queries
    ):
        ValidationFactory.create_batch(10, user=normal_user)
        with django_assert_max_num_queries(9):
            res = client_authenticated_user.get(reverse("validation-list"))
            assert res.status_code == 200
            assert len(res.json()) == 10
            first = res.json()[0]
            assert "id" in first
            assert "filename" in first
            assert "status" in first
            assert "platform_name" in first
            assert "validation_result" in first
            assert "created" in first
            assert "platform" in first
            assert "result_data" not in first
            assert "error_message" in first
            assert "file_size" in first
            assert "cop_version" in first
            assert "report_code" in first
            assert "api_key_prefix" in first

    def test_validation_list_other_users(
        self, client_authenticated_user, normal_user, django_assert_max_num_queries
    ):
        ValidationFactory.create_batch(3, user=normal_user)
        ValidationFactory.create_batch(5)  # new users will be created for those
        with django_assert_max_num_queries(9):
            res = client_authenticated_user.get(reverse("validation-list"))
            assert res.status_code == 200
            assert len(res.json()) == 3

    def test_validation_detail(
        self, client_authenticated_user, normal_user, django_assert_max_num_queries
    ):
        v = ValidationFactory(user=normal_user)
        with django_assert_max_num_queries(9):
            res = client_authenticated_user.get(reverse("validation-detail", args=[v.pk]))
            assert res.status_code == 200
            data = res.json()
            assert "id" in data
            assert "filename" in data
            assert "status" in data
            assert "platform_name" in data
            assert "validation_result" in data
            assert "created" in data
            assert "platform" in data
            assert "result_data" in data
            assert "error_message" in data
            assert "file_size" in data
            assert "cop_version" in data
            assert "report_code" in data
            assert "api_key_prefix" in data

    def test_validation_delete_preserves_core(self, client_authenticated_user, normal_user):
        """
        Test that when deleting a validation through the API, the core is preserved.
        """
        v = ValidationFactory(user=normal_user)
        core_id = v.core_id
        assert core_id is not None
        assert Validation.objects.filter(pk=v.pk).exists()

        res = client_authenticated_user.delete(reverse("validation-detail", args=[v.pk]))
        assert res.status_code == 204

        assert not Validation.objects.filter(pk=v.pk).exists()
        assert ValidationCore.objects.filter(pk=core_id).exists()

    def test_validation_list_with_api_key(self, client_with_api_key, normal_user):
        ValidationFactory.create_batch(10, user=normal_user)
        res = client_with_api_key.get(reverse("validation-list"))
        assert res.status_code == 200
        assert len(res.json()) == 10

    def test_create_with_api_key(self, client_with_api_key, normal_user):
        filename = "tr.json"
        file = SimpleUploadedFile(filename, content=b"xxx")
        with patch("validations.tasks.validate_file.delay_on_commit") as p:
            res = client_with_api_key.post(
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
        assert val.user == normal_user
        assert val.core.api_key_prefix == client_with_api_key.api_key_prefix_
        assert val.core.api_key_prefix == res.json()["api_key_prefix"]


@pytest.mark.django_db
class TestValidationAPIThrottling:
    def test_list_with_api_key(self, client_with_api_key, normal_user, settings):
        settings.REST_FRAMEWORK["DEFAULT_THROTTLE_RATES"]["api_keys"] = "1/minute"
        ValidationFactory.create_batch(10, user=normal_user)
        res = client_with_api_key.get(reverse("validation-list"))
        assert res.status_code == 200
        assert len(res.json()) == 10
        # second request should be throttled
        res = client_with_api_key.get(reverse("validation-list"))
        assert res.status_code == 429
        assert "Request was throttled" in res.json()["detail"]

    def test_list_as_normal_user(self, client_authenticated_user, normal_user, settings):
        """
        Normal access (with cookie based authentication) should not be throttled.
        """
        settings.REST_FRAMEWORK["DEFAULT_THROTTLE_RATES"]["api_keys"] = "1/minute"
        ValidationFactory.create_batch(10, user=normal_user)
        res = client_authenticated_user.get(reverse("validation-list"))
        assert res.status_code == 200
        assert len(res.json()) == 10
        # second request should not be throttled
        res = client_authenticated_user.get(reverse("validation-list"))
        assert res.status_code == 200
        assert len(res.json()) == 10


@pytest.mark.django_db
class TestCounterAPIValidationAPI:
    def test_create(self, client_authenticated_user):
        data = factory.build(dict, FACTORY_CLASS=CounterAPIValidationRequestDataFactory)
        with patch("validations.tasks.validate_counter_api.delay_on_commit") as p:
            res = client_authenticated_user.post(
                reverse("counter-api-validation-list"),
                data=data,
                format="json",
            )
            assert res.status_code == 201
            p.assert_called_once_with(UUID(res.json()["id"]))
        val = Validation.objects.select_related("core").get()
        assert str(val.pk) == res.json()["id"]
        assert "url" in res.json()
        assert "credentials" in res.json()
        assert "requested_cop_version" in res.json()
        assert "cop_version" in res.json()
        assert "requested_report_code" in res.json()
        assert "report_code" in res.json()
        assert "api_endpoint" in res.json()
        assert "requested_extra_attributes" in res.json()
        assert "requested_begin_date" in res.json()
        assert "requested_end_date" in res.json()

    @pytest.mark.parametrize(
        ["empty_credential_fields", "status_code"],
        [
            [[], 201],
            [["requestor_id"], 201],
            [["customer_id"], 400],  # customer_id is required
            [["api_key"], 201],
            [["requestor_id", "customer_id"], 400],
            [["requestor_id", "api_key"], 201],
            [["customer_id", "api_key"], 400],
            [["requestor_id", "customer_id", "api_key"], 400],
        ],
    )
    def test_create_with_empty_credential_fields(
        self, client_authenticated_user, empty_credential_fields, status_code
    ):
        data = factory.build(dict, FACTORY_CLASS=CounterAPIValidationRequestDataFactory)
        for field in empty_credential_fields:
            data["credentials"][field] = ""
        with patch("validations.tasks.validate_counter_api.delay_on_commit"):
            res = client_authenticated_user.post(
                reverse("counter-api-validation-list"),
                data=data,
                format="json",
            )
            assert res.status_code == status_code
