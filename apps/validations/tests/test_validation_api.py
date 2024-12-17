from datetime import timedelta
from unittest.mock import patch
from uuid import UUID, uuid4

import factory
import pytest
from core.fake_data import UserFactory
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from django.utils.timezone import now

from validations.enums import SeverityLevel
from validations.fake_data import (
    CounterAPICredentialsFactory,
    CounterAPIValidationFactory,
    CounterAPIValidationRequestDataFactory,
    ValidationFactory,
    ValidationMessageFactory,
)
from validations.models import CounterAPIValidation, Validation, ValidationCore


@pytest.mark.django_db
class TestFileValidationAPI:
    def test_create(self, client_authenticated_user, settings):
        settings.VALIDATION_LIFETIME = 1
        filename = "tr.json"
        file = SimpleUploadedFile(filename, content=b"xxx")
        with patch("validations.tasks.validate_file.delay_on_commit") as p:
            res = client_authenticated_user.post(
                reverse("validation-file"),
                data={"file": file, "user_note": "test"},
                format="multipart",
            )
            p.assert_called_once_with(UUID(res.json()["id"]))
        assert res.status_code == 201
        assert res.json()["filename"] == filename
        val = Validation.objects.select_related("core").get()
        assert val.filename == filename
        assert val.user_note == "test"
        assert str(val.pk) == res.json()["id"]
        assert (
            res.json()["expiration_date"][:16]
            == (val.core.created + timedelta(days=1)).isoformat()[:16]
        ), "We only compare the first 16 characters"

    def test_create_with_empty_file(self, client_authenticated_user):
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

    def test_create_with_too_large_a_file(self, settings, client_authenticated_user):
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

    def test_validation_list(
        self, client_authenticated_user, normal_user, django_assert_max_num_queries
    ):
        ValidationFactory.create_batch(10, user=normal_user)
        with django_assert_max_num_queries(9):
            res = client_authenticated_user.get(reverse("validation-list"), {"page_size": 8})
            assert res.status_code == 200
            assert "count" in res.json()
            assert "next" in res.json()
            assert "results" in res.json()
            assert len(res.json()["results"]) == 8
            first = res.json()["results"][0]
            assert "id" in first
            assert "filename" in first
            assert "file_url" in first
            assert "status" in first
            assert "user_note" in first
            assert "validation_result" in first
            assert "created" in first
            assert "result_data" not in first
            assert "error_message" in first
            assert "file_size" in first
            assert "cop_version" in first
            assert "report_code" in first
            assert "api_key_prefix" in first
            assert "data_source" in first
            assert "expiration_date" in first
            assert "public_id" in first

    def test_validation_list_other_users(
        self, client_authenticated_user, normal_user, django_assert_max_num_queries
    ):
        ValidationFactory.create_batch(3, user=normal_user)
        ValidationFactory.create_batch(5)  # new users will be created for those
        with django_assert_max_num_queries(9):
            res = client_authenticated_user.get(reverse("validation-list"))
            assert res.status_code == 200
            assert res.json()["count"] == 3

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
            assert "file_url" in data
            assert "status" in data
            assert "user_note" in data
            assert "validation_result" in data
            assert "created" in data
            assert "result_data" in data
            assert "error_message" in data
            assert "file_size" in data
            assert "cop_version" in data
            assert "report_code" in data
            assert "api_key_prefix" in data
            assert "data_source" in data
            assert "expiration_date" in data
            assert "public_id" in data

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

    @pytest.mark.parametrize("method", ["put", "patch"])
    def test_validation_update_not_allowed(self, client_authenticated_user, normal_user, method):
        v = ValidationFactory(user=normal_user)
        res = getattr(client_authenticated_user, method)(
            reverse("validation-detail", args=[v.pk]), data={}, format="json"
        )
        assert res.status_code == 405

    def test_validation_list_with_api_key(self, client_with_api_key, normal_user):
        ValidationFactory.create_batch(10, user=normal_user)
        res = client_with_api_key.get(reverse("validation-list"))
        assert res.status_code == 200
        assert res.json()["count"] == 10

    def test_create_with_api_key(self, client_with_api_key, normal_user):
        filename = "tr.json"
        file = SimpleUploadedFile(filename, content=b"xxx")
        with patch("validations.tasks.validate_file.delay_on_commit") as p:
            res = client_with_api_key.post(
                reverse("validation-file"),
                data={"file": file, "user_note": "test"},
                format="multipart",
            )
            p.assert_called_once_with(UUID(res.json()["id"]))
        assert res.status_code == 201
        assert res.json()["filename"] == filename
        val = Validation.objects.select_related("core").get()
        assert val.filename == filename
        assert val.user_note == "test"
        assert str(val.pk) == res.json()["id"]
        assert val.user == normal_user
        assert val.core.api_key_prefix == client_with_api_key.api_key_prefix_
        assert val.core.api_key_prefix == res.json()["api_key_prefix"]

    def test_validation_stats(self, client_authenticated_user, normal_user):
        v = ValidationFactory.create(user=normal_user)
        ValidationMessageFactory.create(validation=v, severity=SeverityLevel.ERROR, summary="Aaa")
        ValidationMessageFactory.create_batch(
            2, validation=v, severity=SeverityLevel.NOTICE, summary="Bbb"
        )
        ValidationMessageFactory.create_batch(
            3, validation=v, severity=SeverityLevel.NOTICE, summary="Ccc"
        )
        res = client_authenticated_user.get(reverse("validation-stats", args=[v.pk]))
        assert res.status_code == 200
        assert "summary" in res.json()
        assert res.json()["summary"] == {
            "Aaa": 1,
            "Bbb": 2,
            "Ccc": 3,
        }
        assert "summary_severity" in res.json()
        assert res.json()["summary_severity"] == [
            {"summary": "Aaa", "severity": "Error", "count": 1},
            {"summary": "Ccc", "severity": "Notice", "count": 3},
            {"summary": "Bbb", "severity": "Notice", "count": 2},
        ]

    def test_list_with_expired_validations(self, client_authenticated_user, normal_user):
        ValidationFactory.create_batch(3, user=normal_user)
        ValidationFactory.create_batch(
            5, user=normal_user, core__expiration_date=now() - timedelta(hours=1)
        )
        res = client_authenticated_user.get(reverse("validation-list"))
        assert res.status_code == 200
        assert res.json()["count"] == 3

    def test_list_with_unexpirable_validations(
        self, client_authenticated_user, normal_user, settings
    ):
        settings.VALIDATION_LIFETIME = 0
        ValidationFactory.create_batch(3, user=normal_user)
        res = client_authenticated_user.get(reverse("validation-list"))
        assert res.status_code == 200
        assert res.json()["count"] == 3

    @pytest.mark.parametrize(
        ["query", "expected_count"], [["5", 1], ["5,5.1", 3], ["5.1", 2], ["", 3]]
    )
    def test_list_filters_cop_version(
        self, client_authenticated_user, normal_user, query, expected_count
    ):
        ValidationFactory.create_batch(1, user=normal_user, core__cop_version="5")
        ValidationFactory.create_batch(2, user=normal_user, core__cop_version="5.1")
        res = client_authenticated_user.get(reverse("validation-list"), {"cop_version": query})
        assert res.status_code == 200
        assert res.json()["count"] == expected_count

    def test_list_filters_validation_result(self, client_authenticated_user, normal_user):
        vs_notice = ValidationFactory.create_batch(3, user=normal_user)
        for v in vs_notice:
            # validation result is set in `save()` method, so we need to set it after creation
            v.core.validation_result = SeverityLevel.NOTICE
            v.core.save()
        vs_error = ValidationFactory.create_batch(5, user=normal_user)
        for v in vs_error:
            v.core.validation_result = SeverityLevel.ERROR
            v.core.save()

        res = client_authenticated_user.get(
            reverse("validation-list"), {"validation_result": SeverityLevel.NOTICE.label}
        )
        assert res.status_code == 200
        assert res.json()["count"] == 3
        # test with multiple values
        res = client_authenticated_user.get(
            reverse("validation-list"),
            {"validation_result": f"{SeverityLevel.ERROR.label},{SeverityLevel.NOTICE.label}"},
        )
        assert res.status_code == 200
        assert res.json()["count"] == 8

    @pytest.mark.parametrize(
        ["query", "expected_count"], [["TR", 1], ["TR,DR", 3], ["", 3], ["DR", 2]]
    )
    def test_list_filters_by_report_code(
        self, client_authenticated_user, normal_user, query, expected_count
    ):
        ValidationFactory.create_batch(1, user=normal_user, core__report_code="TR")
        ValidationFactory.create_batch(2, user=normal_user, core__report_code="DR")
        res = client_authenticated_user.get(reverse("validation-list"), {"report_code": query})
        assert res.status_code == 200
        assert res.json()["count"] == expected_count

    @pytest.mark.parametrize(
        ["query", "expected_count"],
        [
            ["/members", 1],
            ["/status", 2],
            ["/reports/[id]", 3],
            ["", 6],
            ["/status,/reports/[id]", 5],
        ],
    )
    def test_list_filters_by_api_endpoint(
        self, client_authenticated_user, normal_user, query, expected_count
    ):
        CounterAPIValidationFactory.create_batch(1, user=normal_user, core__api_endpoint="/members")
        CounterAPIValidationFactory.create_batch(2, user=normal_user, core__api_endpoint="/status")
        CounterAPIValidationFactory.create_batch(
            3, user=normal_user, core__api_endpoint="/reports/[id]"
        )
        res = client_authenticated_user.get(reverse("validation-list"), {"api_endpoint": query})
        assert res.status_code == 200
        assert res.json()["count"] == expected_count

    @pytest.mark.parametrize(
        ["query", "expected_count"],
        [["file", 1], ["counter_api", 2], ["", 3], ["file,counter_api", 3]],
    )
    def test_list_filters_by_data_source(
        self, client_authenticated_user, normal_user, query, expected_count
    ):
        v = ValidationFactory.create_batch(1, user=normal_user)
        cvs = CounterAPIValidationFactory.create_batch(2, user=normal_user)
        assert v[0].core.sushi_credentials_checksum == ""
        assert all(c.core.sushi_credentials_checksum != "" for c in cvs)
        res = client_authenticated_user.get(reverse("validation-list"), {"data_source": query})
        assert res.status_code == 200
        assert res.json()["count"] == expected_count

    @pytest.mark.parametrize(["published", "expected_count"], [(True, 1), (False, 3), (None, 4)])
    def test_list_filters_by_published(
        self, client_authenticated_user, normal_user, published, expected_count
    ):
        ValidationFactory.create_batch(3, user=normal_user)
        ValidationFactory.create(user=normal_user, public_id=uuid4())
        res = client_authenticated_user.get(
            reverse("validation-list"), {"published": published} if published is not None else {}
        )
        assert res.status_code == 200
        assert res.json()["count"] == expected_count

    @pytest.mark.parametrize("desc", [True, False])
    @pytest.mark.parametrize(
        "attr",
        [
            "cop_version",
            "created",
            "expiration_date",
            "file_size",
            "filename",
            "user_note",
            "report_code",
            "status",
            "validation_result",
        ],
    )
    def test_list_filters_order_by(self, client_authenticated_user, normal_user, desc, attr):
        ValidationFactory.create_batch(3, user=normal_user)
        res = client_authenticated_user.get(
            reverse("validation-list"), {"order_by": attr, "order_desc": desc}
        )
        assert res.status_code == 200
        assert res.json()["count"] == 3
        if desc:
            assert res.json()["results"][0][attr] >= res.json()["results"][-1][attr]
        else:
            assert res.json()["results"][0][attr] <= res.json()["results"][-1][attr]

    def test_validation_publish(self, client_authenticated_user, normal_user):
        v = ValidationFactory.create(user=normal_user)
        assert v.public_id is None
        res = client_authenticated_user.post(reverse("validation-publish", args=[v.pk]))
        assert res.status_code == 200
        v.refresh_from_db()
        assert v.public_id is not None
        assert str(v.public_id) == res.json()["public_id"]

    def test_validation_unpublish(self, client_authenticated_user, normal_user):
        v = ValidationFactory.create(user=normal_user)
        v.publish()
        assert v.public_id is not None
        res = client_authenticated_user.post(reverse("validation-unpublish", args=[v.pk]))
        assert res.status_code == 200
        v.refresh_from_db()
        assert v.public_id is None
        assert res.json()["public_id"] is None

    def test_validation_publish_unpublish_not_allowed_for_other_users(
        self, client_authenticated_user, normal_user
    ):
        v = ValidationFactory.create(user=UserFactory())  # noqa: F821
        res = client_authenticated_user.post(reverse("validation-publish", args=[v.pk]))
        assert res.status_code == 404
        res = client_authenticated_user.post(reverse("validation-unpublish", args=[v.pk]))
        assert res.status_code == 404


@pytest.mark.django_db
class TestValidationAPIThrottling:
    def test_list_get_with_api_key(self, client_with_api_key, normal_user, settings):
        """
        Test that GET requests are not throttled.
        """
        settings.REST_FRAMEWORK["DEFAULT_THROTTLE_RATES"]["api_keys"] = "1/minute"
        ValidationFactory.create_batch(10, user=normal_user)
        res = client_with_api_key.get(reverse("validation-list"))
        assert res.status_code == 200
        assert res.json()["count"] == 10
        # second request should be throttled
        res = client_with_api_key.get(reverse("validation-list"))
        assert res.status_code == 200, "GET requests should not be throttled"

    def test_list_post_with_api_key(self, client_with_api_key, normal_user, settings):
        settings.REST_FRAMEWORK["DEFAULT_THROTTLE_RATES"]["api_keys"] = "1/minute"

        filename = "tr.json"
        file = SimpleUploadedFile(filename, content=b"xxx")
        with patch("validations.tasks.validate_file.delay_on_commit") as p:
            res = client_with_api_key.post(
                reverse("validation-file"),
                data={"file": file, "user_note": "test"},
                format="multipart",
            )
            p.assert_called_once_with(UUID(res.json()["id"]))
            assert res.status_code == 201

        # second request should be throttled
        with patch("validations.tasks.validate_file.delay_on_commit") as p:
            res = client_with_api_key.post(
                reverse("validation-file"),
                data={"file": file, "user_note": "test"},
                format="multipart",
            )
            p.assert_not_called()
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
        assert res.json()["count"] == 10
        # second request should not be throttled
        res = client_authenticated_user.get(reverse("validation-list"))
        assert res.status_code == 200
        assert res.json()["count"] == 10


@pytest.mark.django_db
class TestCounterAPIValidationAPI:
    @pytest.mark.parametrize("expiration_days", [1, 3, 7])
    def test_create(self, client_authenticated_user, expiration_days, settings):
        settings.VALIDATION_LIFETIME = expiration_days
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
        out = res.json()
        assert str(val.pk) == out["id"]
        assert "url" in out
        assert "credentials" in out
        assert "requested_cop_version" in out
        assert "cop_version" in out
        assert "requested_report_code" in out
        assert "report_code" in out
        assert "api_endpoint" in out
        assert "requested_extra_attributes" in out
        assert "requested_begin_date" in out
        assert "requested_end_date" in out
        assert "expiration_date" in out
        assert (
            out["expiration_date"][:16]
            == (val.core.created + timedelta(days=expiration_days)).isoformat()[:16]
        ), "We only compare the first 16 characters"

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

    @pytest.mark.parametrize("platform_present", [True, False])
    def test_create_with_platform_in_credentials(self, client_authenticated_user, platform_present):
        data = factory.build(dict, FACTORY_CLASS=CounterAPIValidationRequestDataFactory)
        data["credentials"]["platform"] = "foobar" if platform_present else ""
        with patch("validations.tasks.validate_counter_api.delay_on_commit") as p:
            res = client_authenticated_user.post(
                reverse("counter-api-validation-list"),
                data=data,
                format="json",
            )
            assert res.status_code == 201
            p.assert_called_once_with(UUID(res.json()["id"]))
        val = CounterAPIValidation.objects.select_related("core").get()
        assert str(val.pk) == res.json()["id"]
        if platform_present:
            assert val.credentials["platform"] == "foobar"
        else:
            assert "platform" not in val.credentials

    def test_create_with_attributes_to_show(self, client_authenticated_user):
        data = factory.build(dict, FACTORY_CLASS=CounterAPIValidationRequestDataFactory)
        data["extra_attributes"] = {"foo": "bar", "attributes_to_show": "YOP|Data_Type"}
        with patch("validations.tasks.validate_counter_api.delay_on_commit") as p:
            res = client_authenticated_user.post(
                reverse("counter-api-validation-list"),
                data=data,
                format="json",
            )
            assert res.status_code == 201
            p.assert_called_once_with(UUID(res.json()["id"]))
        val = CounterAPIValidation.objects.select_related("core").get()
        assert str(val.pk) == res.json()["id"]
        assert val.requested_extra_attributes == {
            "foo": "bar",
            "attributes_to_show": "YOP|Data_Type",
        }

    @pytest.mark.parametrize("endpoint", ["/members", "/status", "/reports"])
    def test_create_for_other_endpoints(self, client_authenticated_user, endpoint):
        credentials_data = factory.build(dict, FACTORY_CLASS=CounterAPICredentialsFactory)
        data = {
            "credentials": credentials_data,
            "api_endpoint": endpoint,
            "cop_version": "5",
            "url": "https://example.com",
        }
        with patch("validations.tasks.validate_counter_api.delay_on_commit") as p:
            res = client_authenticated_user.post(
                reverse("counter-api-validation-list"),
                data=data,
                format="json",
            )
            assert res.status_code == 201
            p.assert_called_once_with(UUID(res.json()["id"]))
        val = CounterAPIValidation.objects.select_related("core").get()
        assert str(val.pk) == res.json()["id"]
        assert val.core.api_endpoint == endpoint
        assert val.requested_report_code == ""
        assert val.requested_begin_date is None
        assert val.requested_end_date is None

    def test_detail_for_generic_validation_api(self, client_authenticated_user, normal_user):
        val = CounterAPIValidationFactory(user=normal_user)
        res = client_authenticated_user.get(reverse("validation-detail", args=[val.pk]))
        assert res.status_code == 200
        data = res.json()
        assert "id" in data
        assert "url" in data
        assert "credentials" in data
        assert data["credentials"] == val.credentials
        assert "requested_cop_version" in data
        assert "cop_version" in data
        assert "requested_report_code" in data
        assert "report_code" in data
        assert "api_endpoint" in data
        assert "requested_extra_attributes" in data
        assert "requested_begin_date" in data
        assert "requested_end_date" in data

    def test_create_with_api_key(self, client_with_api_key, normal_user):
        data = factory.build(dict, FACTORY_CLASS=CounterAPIValidationRequestDataFactory)
        with patch("validations.tasks.validate_counter_api.delay_on_commit") as p:
            res = client_with_api_key.post(
                reverse("counter-api-validation-list"),
                data=data,
                format="json",
            )
            assert res.status_code == 201
            p.assert_called_once_with(UUID(res.json()["id"]))
        val = Validation.objects.select_related("core").get()
        assert str(val.pk) == res.json()["id"]
        assert val.user == normal_user
        assert val.core.api_key_prefix == client_with_api_key.api_key_prefix_
        assert val.core.api_key_prefix == res.json()["api_key_prefix"]

    def test_list_with_expired_validations(self, client_authenticated_user, normal_user):
        CounterAPIValidationFactory.create_batch(3, user=normal_user)
        CounterAPIValidationFactory.create_batch(
            5, user=normal_user, core__expiration_date=now() - timedelta(hours=1)
        )
        res = client_authenticated_user.get(reverse("validation-list"))
        assert res.status_code == 200
        assert res.json()["count"] == 3


@pytest.mark.django_db
class TestValidationMessagesAPI:
    def test_list(self, client_authenticated_user, normal_user):
        val = ValidationFactory(user=normal_user, messages__count=3)
        ValidationFactory(user=normal_user, messages__count=5)  # other validation, not in output
        res = client_authenticated_user.get(reverse("validation-message-list", args=[val.pk]))
        assert res.status_code == 200
        out = res.json()
        assert "count" in out, "count should be in the response - it should be paginated"
        assert "next" in out, "next should be in the response - it should be paginated"
        assert "previous" in out, "previous should be in the response - it should be paginated"
        assert "results" in out, "results should be in the response - it should be paginated"
        assert len(out["results"]) == 3
        first = out["results"][0]
        assert "message" in first
        assert "severity" in first
        assert "summary" in first
        assert "hint" in first
        assert "location" in first
        assert "data" in first

    def test_detail(self, client_authenticated_user, normal_user):
        val = ValidationFactory(user=normal_user, messages__count=3)
        ValidationFactory(user=normal_user, messages__count=5)
        m = val.messages.first()
        res = client_authenticated_user.get(
            reverse("validation-message-detail", args=[val.pk, m.pk])
        )
        assert res.status_code == 200
        out = res.json()
        assert "message" in out
        assert "severity" in out
        assert "summary" in out
        assert "hint" in out
        assert "location" in out
        assert "data" in out

    @pytest.mark.parametrize("page_size", [5, 8, 10, 15])
    def test_list_pagination(self, client_authenticated_user, normal_user, page_size):
        val = ValidationFactory(user=normal_user, messages__count=10)
        res = client_authenticated_user.get(
            reverse("validation-message-list", args=[val.pk]), {"page_size": page_size}
        )
        assert res.status_code == 200
        out = res.json()
        assert "count" in out, "count should be in the response - it should be paginated"
        assert "next" in out, "next should be in the response - it should be paginated"
        assert "previous" in out, "previous should be in the response - it should be paginated"
        assert "results" in out, "results should be in the response - it should be paginated"
        assert len(out["results"]) == min(page_size, 10)

    @pytest.mark.parametrize("order_desc", [True, False])
    @pytest.mark.parametrize("order_by", ["summary", "hint", "location"])
    def test_list_ordering(self, client_authenticated_user, normal_user, order_by, order_desc):
        val = ValidationFactory(user=normal_user, messages__count=10)
        res = client_authenticated_user.get(
            reverse("validation-message-list", args=[val.pk]),
            {"order_by": order_by, "order_desc": order_desc},
        )
        assert res.status_code == 200
        out = res.json()
        assert len(out["results"]) == 10
        if order_desc:
            assert out["results"][0][order_by] >= out["results"][-1][order_by]
        else:
            assert out["results"][0][order_by] <= out["results"][-1][order_by]

    @pytest.mark.parametrize("order_desc", [True, False])
    def test_list_ordering_by_severity(self, client_authenticated_user, normal_user, order_desc):
        """
        Severity needs to be decoded back to the enum value to be able to compare it,
        so it has a separate test
        """
        val = ValidationFactory(user=normal_user, messages__count=10)
        res = client_authenticated_user.get(
            reverse("validation-message-list", args=[val.pk]),
            {"order_by": "severity", "order_desc": order_desc},
        )
        assert res.status_code == 200
        out = res.json()
        assert len(out["results"]) == 10
        first_value = SeverityLevel.by_any_value(out["results"][0]["severity"])
        last_value = SeverityLevel.by_any_value(out["results"][-1]["severity"])
        if order_desc:
            assert first_value >= last_value
        else:
            assert first_value <= last_value

    @pytest.mark.parametrize("severity", [SeverityLevel.ERROR, SeverityLevel.WARNING])
    @pytest.mark.parametrize("encoding", ["value", "name", "label"])
    def test_list_filtering_by_severity(
        self, client_authenticated_user, normal_user, severity, encoding
    ):
        val = ValidationFactory(user=normal_user)
        ValidationMessageFactory.create_batch(3, validation=val, severity=severity)
        ValidationMessageFactory.create_batch(1, validation=val, severity=SeverityLevel.NOTICE)
        ValidationMessageFactory.create_batch(
            2, validation=val, severity=SeverityLevel.CRITICAL_ERROR
        )
        res = client_authenticated_user.get(
            reverse("validation-message-list", args=[val.pk]),
            {"severity": getattr(severity, encoding)},
        )
        assert res.status_code == 200
        out = res.json()
        assert len(out["results"]) == 3
        for r in out["results"]:
            assert r["severity"] == severity.label
        # test with list
        res = client_authenticated_user.get(
            reverse("validation-message-list", args=[val.pk]),
            {"severity": f"{getattr(severity, encoding)},{SeverityLevel.NOTICE.label}"},
        )
        assert res.status_code == 200
        assert len(res.json()) == 4


@pytest.mark.django_db
class TestPublicValidationAPI:
    def test_list_is_forbidden(self, client):
        res = client.get(reverse("public-validation-list"))
        assert res.status_code == 403

    def test_detail(self, client):
        val = CounterAPIValidationFactory(public_id=uuid4())
        assert val.credentials is not None
        res = client.get(reverse("public-validation-detail", args=[val.public_id]))
        assert res.status_code == 200
        out = res.json()
        assert "id" in out
        assert "url" in out
        assert "credentials" in out
        assert "requested_cop_version" in out
        assert "cop_version" in out
        assert "requested_report_code" in out
        assert "report_code" in out
        assert "api_endpoint" in out
        assert "requested_extra_attributes" in out
        assert "requested_begin_date" in out
        assert "requested_end_date" in out
        assert out["credentials"] is None, "credentials should not be exposed"
