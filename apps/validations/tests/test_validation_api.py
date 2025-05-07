from datetime import timedelta
from unittest.mock import patch
from urllib.parse import parse_qs, urlsplit
from uuid import UUID, uuid4

import factory
import pytest
from core.fake_data import UserFactory
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from django.utils.timezone import now

import validations.tasks
from validations.enums import SeverityLevel
from validations.fake_data import (
    CounterAPICredentialsFactory,
    CounterAPIValidationFactory,
    CounterAPIValidationRequestDataFactory,
    ValidationFactory,
    ValidationMessageFactory,
)
from validations.models import CounterAPIValidation, Validation, ValidationCore

expected_validation_keys = {
    "api_endpoint",
    "api_key_prefix",
    "cop_version",
    "created",
    "credentials",
    "data_source",
    "error_message",
    "expiration_date",
    "file_size",
    "file_url",
    "filename",
    "id",
    "public_id",
    "report_code",
    "requested_begin_date",
    "requested_cop_version",
    "requested_end_date",
    "requested_extra_attributes",
    "requested_report_code",
    "stats",
    "status",
    "url",
    "use_short_dates",
    "user_note",
    "validation_result",
}

expected_validation_keys_detail = expected_validation_keys | {"result_data", "user", "full_url"}


@pytest.mark.django_db
class TestValidationAPI:
    """
    This is a set of tests for the validation API which is shared by the file
    and COUNTER API validations. Thus it does not test the actual creation
    of those validations, which is tested in separate classes below.
    """

    def test_validation_list(
        self, client_authenticated_user, normal_user, django_assert_max_num_queries
    ):
        ValidationFactory.create_batch(10, core__user=normal_user)
        with django_assert_max_num_queries(9):
            res = client_authenticated_user.get(reverse("validation-list"), {"page_size": 8})
            assert res.status_code == 200
            assert "count" in res.json()
            assert "next" in res.json()
            assert "results" in res.json()
            assert len(res.json()["results"]) == 8
            first = res.json()["results"][0]
            assert set(first.keys()) == expected_validation_keys

    def test_validation_list_other_users(
        self, client_authenticated_user, normal_user, django_assert_max_num_queries
    ):
        ValidationFactory.create_batch(3, core__user=normal_user)
        ValidationFactory.create_batch(5)  # new users will be created for those
        with django_assert_max_num_queries(9):
            res = client_authenticated_user.get(reverse("validation-list"))
            assert res.status_code == 200
            assert res.json()["count"] == 3

    def test_validation_detail(
        self, client_authenticated_user, normal_user, django_assert_max_num_queries
    ):
        v = ValidationFactory(core__user=normal_user)
        with django_assert_max_num_queries(9):
            res = client_authenticated_user.get(reverse("validation-detail", args=[v.pk]))
            assert res.status_code == 200
            data = res.json()
            assert set(data.keys()) == expected_validation_keys_detail
            assert data["data_source"] == "file"
            assert "full_url" in data
            assert data["full_url"] == ""

    def test_validation_detail_using_api_key(self, client_with_api_key, normal_user):
        v = ValidationFactory(core__user=normal_user)
        res = client_with_api_key.get(reverse("validation-detail", args=[v.pk]))
        assert res.status_code == 200
        data = res.json()
        assert set(data.keys()) == expected_validation_keys_detail

    def test_validation_detail_counter_api(
        self, client_authenticated_user, normal_user, django_assert_max_num_queries
    ):
        v = CounterAPIValidationFactory(core__user=normal_user)
        with django_assert_max_num_queries(9):
            res = client_authenticated_user.get(reverse("validation-detail", args=[v.pk]))
            assert res.status_code == 200
            data = res.json()
            assert set(data.keys()) == expected_validation_keys_detail
            assert data["data_source"] == "counter_api"
            assert "full_url" in data
            assert data["full_url"] == v.get_url()

    def test_validation_detail_other_users(self, client_authenticated_user):
        v = ValidationFactory()  # this belongs to some randomly created user
        res = client_authenticated_user.get(reverse("validation-detail", args=[v.pk]))
        assert res.status_code == 404, "user who is not an owner should not have access"

    def test_validation_detail_admin(self, client_validator_admin_user, normal_user):
        v = ValidationFactory(core__user=normal_user)
        res = client_validator_admin_user.get(reverse("validation-detail", args=[v.pk]))
        assert res.status_code == 200, "admin can see validation details"

    def test_validation_detail_superuser(self, client_su_user, normal_user):
        v = ValidationFactory(core__user=normal_user)
        res = client_su_user.get(reverse("validation-detail", args=[v.pk]))
        assert res.status_code == 200, "superuser can see validation details"

    def test_validation_delete_preserves_core(self, client_authenticated_user, normal_user):
        """
        Test that when deleting a validation through the API, the core is preserved.
        """
        v = ValidationFactory(core__user=normal_user)
        core_id = v.core_id
        assert core_id is not None
        assert Validation.objects.filter(pk=v.pk).exists()

        res = client_authenticated_user.delete(reverse("validation-detail", args=[v.pk]))
        assert res.status_code == 204

        assert not Validation.objects.filter(pk=v.pk).exists()
        assert ValidationCore.objects.filter(pk=core_id).exists()

    @pytest.mark.parametrize(
        ["user_type", "status_code"],
        [
            ("unauthenticated", 403),
            ("normal", 404),
            ("su", 204),
            ("admin", 204),
            ("api_key_normal", 404),
            ("api_key_admin", 204),
        ],
    )
    def test_validation_delete_not_allowed_for_other_users(
        self, users_and_clients, user_type, status_code
    ):
        user, client = users_and_clients[user_type]
        v = ValidationFactory()  # this belongs to some randomly created user
        res = client.delete(reverse("validation-detail", args=[v.pk]))
        assert res.status_code == status_code

    @pytest.mark.parametrize("method", ["put", "patch"])
    def test_validation_update_not_allowed(self, client_authenticated_user, normal_user, method):
        v = ValidationFactory(core__user=normal_user)
        res = getattr(client_authenticated_user, method)(
            reverse("validation-detail", args=[v.pk]), data={}, format="json"
        )
        assert res.status_code == 405

    def test_validation_list_with_api_key(self, client_with_api_key, normal_user):
        ValidationFactory.create_batch(10, core__user=normal_user)
        res = client_with_api_key.get(reverse("validation-list"))
        assert res.status_code == 200
        assert res.json()["count"] == 10

    def test_validation_stats(self, client_authenticated_user, normal_user):
        v = ValidationFactory.create(core__user=normal_user)
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
        ValidationFactory.create_batch(3, core__user=normal_user)
        ValidationFactory.create_batch(
            5, core__user=normal_user, core__expiration_date=now() - timedelta(hours=1)
        )
        res = client_authenticated_user.get(reverse("validation-list"))
        assert res.status_code == 200
        assert res.json()["count"] == 3

    def test_list_with_unexpirable_validations(
        self, client_authenticated_user, normal_user, settings
    ):
        settings.VALIDATION_LIFETIME = 0
        ValidationFactory.create_batch(3, core__user=normal_user)
        res = client_authenticated_user.get(reverse("validation-list"))
        assert res.status_code == 200
        assert res.json()["count"] == 3

    @pytest.mark.parametrize(
        ["query", "expected_count"], [["5", 1], ["5,5.1", 3], ["5.1", 2], ["", 3]]
    )
    def test_list_filters_cop_version(
        self, client_authenticated_user, normal_user, query, expected_count
    ):
        ValidationFactory.create_batch(1, core__user=normal_user, core__cop_version="5")
        ValidationFactory.create_batch(2, core__user=normal_user, core__cop_version="5.1")
        res = client_authenticated_user.get(reverse("validation-list"), {"cop_version": query})
        assert res.status_code == 200
        assert res.json()["count"] == expected_count

    @pytest.mark.parametrize(
        ["results", "expected_count"],
        [
            ([SeverityLevel.UNKNOWN], 1),
            ([SeverityLevel.PASSED], 2),
            ([SeverityLevel.NOTICE], 3),
            ([SeverityLevel.WARNING], 4),
            ([SeverityLevel.ERROR], 5),
            ([SeverityLevel.CRITICAL_ERROR], 6),
            ([SeverityLevel.FATAL_ERROR], 7),
            ([SeverityLevel.UNKNOWN, SeverityLevel.WARNING], 5),
            ([SeverityLevel.NOTICE, SeverityLevel.ERROR], 8),
            ([], 28),
        ],
    )
    def test_list_filters_validation_result(
        self, client_authenticated_user, normal_user, results, expected_count
    ):
        for i, result in enumerate(SeverityLevel):
            for v in ValidationFactory.create_batch(i + 1, core__user=normal_user):
                v.core.validation_result = result
                v.core.save()

        query = {"validation_result": ",".join(str(r.label) for r in results)} if results else {}
        res = client_authenticated_user.get(reverse("validation-list"), query)
        assert res.status_code == 200
        assert res.json()["count"] == expected_count

    @pytest.mark.parametrize(
        ["query", "expected_count"], [["TR", 1], ["TR,DR", 3], ["", 3], ["DR", 2]]
    )
    def test_list_filters_by_report_code(
        self, client_authenticated_user, normal_user, query, expected_count
    ):
        ValidationFactory.create_batch(1, core__user=normal_user, core__report_code="TR")
        ValidationFactory.create_batch(2, core__user=normal_user, core__report_code="DR")
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
        CounterAPIValidationFactory.create_batch(
            1, core__user=normal_user, core__api_endpoint="/members"
        )
        CounterAPIValidationFactory.create_batch(
            2, core__user=normal_user, core__api_endpoint="/status"
        )
        CounterAPIValidationFactory.create_batch(
            3, core__user=normal_user, core__api_endpoint="/reports/[id]"
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
        v = ValidationFactory.create_batch(1, core__user=normal_user)
        cvs = CounterAPIValidationFactory.create_batch(2, core__user=normal_user)
        assert v[0].core.sushi_credentials_checksum == ""
        assert all(c.core.sushi_credentials_checksum != "" for c in cvs)
        res = client_authenticated_user.get(reverse("validation-list"), {"data_source": query})
        assert res.status_code == 200
        assert res.json()["count"] == expected_count

    @pytest.mark.parametrize(["published", "expected_count"], [(True, 1), (False, 3), (None, 4)])
    def test_list_filters_by_published(
        self, client_authenticated_user, normal_user, published, expected_count
    ):
        ValidationFactory.create_batch(3, core__user=normal_user)
        ValidationFactory.create(core__user=normal_user, public_id=uuid4())
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
        ValidationFactory.create_batch(3, core__user=normal_user)
        res = client_authenticated_user.get(
            reverse("validation-list"), {"order_by": attr, "order_desc": desc}
        )
        assert res.status_code == 200
        assert res.json()["count"] == 3
        if desc:
            assert res.json()["results"][0][attr] >= res.json()["results"][-1][attr]
        else:
            assert res.json()["results"][0][attr] <= res.json()["results"][-1][attr]

    @pytest.mark.parametrize(
        ["query", "expected_count"], [["foo", 1], ["bar", 3], ["baz", 0], ["", 5], [None, 5]]
    )
    def test_list_filters_by_user_note(
        self, client_authenticated_user, normal_user, query, expected_count
    ):
        ValidationFactory.create_batch(3, core__user=normal_user, user_note="barakuda")
        ValidationFactory.create(core__user=normal_user, user_note="fooo")
        ValidationFactory.create(core__user=normal_user, user_note="whatever")
        res = client_authenticated_user.get(
            reverse("validation-list"), {"search": query} if query is not None else {}
        )
        assert res.status_code == 200
        assert res.json()["count"] == expected_count

    @pytest.mark.parametrize("endpoint", ["validation-list", "validation-list-all"])
    def test_list_filter_by_user_name_is_only_applied_for_all_endpoint(
        self, client_su_user, endpoint, su_user
    ):
        """
        Test that when superuser lists all validations, the filter by user attrs is applied.
        But when listing only the user's own validations, the filter is not applied.
        """
        su_user.email = "test@example.com"
        su_user.save()
        ValidationFactory.create(core__user=su_user, user_note="fooo")
        ValidationFactory.create(core__user=su_user, user_note="whatever")
        res = client_su_user.get(reverse(endpoint), {"search": "example"})
        assert res.status_code == 200
        if endpoint == "validation-list-all":
            assert res.json()["count"] == 2, "All validations should be visible"
        else:
            assert res.json()["count"] == 0, "No validation with example in user_note or filename"

    def test_list_filter_by_user_name_is_only_applied_for_all_endpoint_normal_user(
        self, client_authenticated_user, normal_user
    ):
        """
        Test that when normal user lists his own validations, the filter by user attrs is not
        applied.
        (normal user cannot see other users' validations)
        """
        normal_user.email = "test@example.com"
        normal_user.save()
        ValidationFactory.create(core__user=normal_user, user_note="fooo")
        ValidationFactory.create(core__user=normal_user, user_note="whatever")
        res = client_authenticated_user.get(reverse("validation-list"), {"search": "example"})
        assert res.status_code == 200
        assert res.json()["count"] == 0, "No validation with example in user_note or filename"

    def test_validation_publish(self, client_authenticated_user, normal_user):
        v = ValidationFactory.create(core__user=normal_user)
        assert v.public_id is None
        res = client_authenticated_user.post(reverse("validation-publish", args=[v.pk]))
        assert res.status_code == 200
        v.refresh_from_db()
        assert v.public_id is not None
        assert str(v.public_id) == res.json()["public_id"]

    def test_validation_unpublish(self, client_authenticated_user, normal_user):
        v = ValidationFactory.create(core__user=normal_user)
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
        v = ValidationFactory.create(core__user=UserFactory())  # noqa: F821
        res = client_authenticated_user.post(reverse("validation-publish", args=[v.pk]))
        assert res.status_code == 404
        res = client_authenticated_user.post(reverse("validation-unpublish", args=[v.pk]))
        assert res.status_code == 404

    def test_all_validations_endpoint_access(self, client_and_status_code_admin_only):
        client, status_code = client_and_status_code_admin_only
        res = client.get(reverse("validation-list-all"))
        assert res.status_code == status_code

    def test_all_validations_endpoint_content(
        self, validator_admin_user, normal_user, client_validator_admin_user
    ):
        ValidationFactory.create_batch(3, core__user=validator_admin_user)
        ValidationFactory.create_batch(2, core__user=normal_user)
        res = client_validator_admin_user.get(reverse("validation-list-all"))
        assert res.status_code == 200
        assert res.json()["count"] == 5
        first = res.json()["results"][0]
        assert set(first.keys()) == expected_validation_keys | {"user"}
        user = first["user"]
        assert set(user.keys()) == {
            "id",
            "email",
            "first_name",
            "last_name",
            "is_active",
            "is_superuser",
            "has_admin_role",
            "is_validator_admin",
        }

    def test_validation_export(self, client_authenticated_user, normal_user):
        v = ValidationFactory.create(core__user=normal_user)
        res = client_authenticated_user.get(reverse("validation-export", args=[v.pk]))
        assert res.status_code == 200
        assert (
            res["Content-Type"]
            == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        assert res["Content-Disposition"].startswith("attachment; filename=validation-")
        assert res["Content-Disposition"].endswith(".xlsx")


@pytest.mark.django_db
class TestFileValidationAPI:
    """
    This part is just for the file part of the validation API, so it only
    deals with the `create` part. The rest is common and is in `TestValidationAPI`.
    """

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
            assert res.status_code == 201
            p.assert_called_once_with(UUID(res.json()["id"]))
        assert res.json()["filename"] == filename
        val = Validation.objects.select_related("core").get()
        assert val.filename == filename
        assert val.user_note == "test"
        assert str(val.pk) == res.json()["id"]
        assert (
            res.json()["expiration_date"][:16]
            == (val.core.created + timedelta(days=1)).isoformat()[:16]
        ), "We only compare the first 16 characters"
        assert res.json()["api_endpoint"] == "", "api_endpoint should be empty for file validations"

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
        settings.FILE_SIZE_LIMITS = {"default": 1023}
        file = SimpleUploadedFile("tr.json", content=b"X" * 1024)
        with patch("validations.tasks.validate_file.delay_on_commit") as p:
            res = client_authenticated_user.post(
                reverse("validation-file"),
                data={"file": file},
                format="multipart",
            )
            p.assert_not_called()
        assert res.status_code == 400
        assert res.json()["file"][0].startswith("Max file size for type")

    def test_create_with_api_key(self, client_with_api_key, normal_user):
        filename = "tr.json"
        file = SimpleUploadedFile(filename, content=b"xxx")
        with patch("validations.tasks.validate_file.delay_on_commit") as p:
            res = client_with_api_key.post(
                reverse("validation-file"),
                data={"file": file, "user_note": "test"},
                format="multipart",
            )
            assert res.status_code == 201
            p.assert_called_once_with(UUID(res.json()["id"]))
        assert res.json()["filename"] == filename
        val = Validation.objects.select_related("core").get()
        assert val.filename == filename
        assert val.user_note == "test"
        assert str(val.pk) == res.json()["id"]
        assert val.core.user == normal_user
        assert val.core.api_key_prefix == client_with_api_key.api_key_prefix_
        assert val.core.api_key_prefix == res.json()["api_key_prefix"]

    def test_create_with_unverified_email(self, client):
        user = UserFactory(verified_email=False)
        client.force_login(user)
        file = SimpleUploadedFile("tr.json", content=b"xxx")
        with patch("validations.tasks.validate_file.delay_on_commit") as p:
            res = client.post(
                reverse("validation-file"),
                data={"file": file},
                format="multipart",
            )
            p.assert_not_called()
            assert res.status_code == 403

    def test_create_with_file_type_limit(self, settings, client_authenticated_user):
        settings.FILE_SIZE_LIMITS = {"default": 1023}
        with open("test_data/reports/50-Sample-TR.json", "rb") as f:
            file = SimpleUploadedFile("tr.json", f.read())
        with patch("validations.tasks.validate_file.delay_on_commit") as p:
            res = client_authenticated_user.post(
                reverse("validation-file"),
                data={"file": file},
                format="multipart",
            )
            p.assert_not_called()
            assert res.status_code == 400
            assert res.json()["file"][0].startswith("Max file size for type 'json' exceeded:")

    def test_create_with_file_type_limit_unknown_type(self, settings, client_authenticated_user):
        settings.FILE_SIZE_LIMITS = {"default": 1023}
        file = SimpleUploadedFile("tr.json", b"x" * 1024)
        with patch("validations.tasks.validate_file.delay_on_commit") as p:
            res = client_authenticated_user.post(
                reverse("validation-file"),
                data={"file": file},
                format="multipart",
            )
            p.assert_not_called()
            assert res.status_code == 400
            assert res.json()["file"][0].startswith("Max file size for type 'default' exceeded:")

    @pytest.mark.parametrize(
        ["filetype", "filename"],
        [
            ("csv", "50-Sample-TR.csv"),
            ("json", "50-Sample-TR.json"),
            ("xlsx", "50-Sample-TR.xlsx"),
            ("csv", "50-Sample-TR.tsv"),
        ],
    )
    def test_create_with_file_type_limit_filetype(
        self, settings, client_authenticated_user, filetype, filename
    ):
        settings.FILE_SIZE_LIMITS = {"default": 1023}
        with open(f"test_data/reports/{filename}", "rb") as f:
            file = SimpleUploadedFile(filename, f.read())
        with patch("validations.tasks.validate_file.delay_on_commit") as p:
            res = client_authenticated_user.post(
                reverse("validation-file"),
                data={"file": file},
                format="multipart",
            )
            p.assert_not_called()
            assert res.status_code == 400
            assert res.json()["file"][0].startswith(
                f"Max file size for type '{filetype}' exceeded:"
            )


@pytest.mark.django_db
class TestCounterAPIValidationAPI:
    @pytest.mark.parametrize("expiration_days", [1, 3, 7])
    def test_create(self, client_authenticated_user, expiration_days, settings):
        settings.VALIDATION_LIFETIME = expiration_days
        data = factory.build(
            dict, FACTORY_CLASS=CounterAPIValidationRequestDataFactory, cop_version="5.1"
        )
        data["user_note"] = "Lorem ipsum"
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
        assert out["requested_cop_version"] == "5.1"
        assert out["cop_version"] == "5.1", "cop_version should be taken from the request"
        assert out["use_short_dates"] is False
        assert out["user_note"] == "Lorem ipsum"

    @pytest.mark.parametrize(
        ["empty_field", "missing", "allowed"],
        [
            ("user_note", True, True),
            ("user_note", False, True),
            ("use_short_dates", True, True),
            ("use_short_dates", False, False),
        ],
    )
    def test_create_with_empty_field(
        self, client_authenticated_user, empty_field, allowed, missing
    ):
        data = factory.build(dict, FACTORY_CLASS=CounterAPIValidationRequestDataFactory)
        if missing:
            del data[empty_field]
        else:
            data[empty_field] = ""
        with patch("validations.tasks.validate_counter_api.delay_on_commit"):
            res = client_authenticated_user.post(
                reverse("counter-api-validation-list"),
                data=data,
                format="json",
            )
            if allowed:
                assert res.status_code == 201
            else:
                assert res.status_code == 400

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
    def test_create_with_empty_credentials_fields(
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
        # make sure that the cop_version is taken from the request because it is not part
        # of the sushi response, so cannot be extracted from there
        assert val.requested_cop_version == "5"
        assert val.core.cop_version == "5"

    def test_detail_for_generic_validation_api(self, client_authenticated_user, normal_user):
        val = CounterAPIValidationFactory(core__user=normal_user)
        res = client_authenticated_user.get(reverse("validation-detail", args=[val.pk]))
        assert res.status_code == 200
        data = res.json()
        assert set(data.keys()) == expected_validation_keys_detail
        assert data["credentials"] == val.credentials

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
        assert val.core.user == normal_user
        assert val.core.api_key_prefix == client_with_api_key.api_key_prefix_
        assert val.core.api_key_prefix == res.json()["api_key_prefix"]

    def test_create_with_unverified_email(self, client):
        user = UserFactory(verified_email=False)
        client.force_login(user)
        data = factory.build(dict, FACTORY_CLASS=CounterAPIValidationRequestDataFactory)
        with patch("validations.tasks.validate_counter_api.delay_on_commit") as p:
            res = client.post(
                reverse("counter-api-validation-list"),
                data=data,
                format="json",
            )
            p.assert_not_called()
            assert res.status_code == 403

    def test_list_with_expired_validations(self, client_authenticated_user, normal_user):
        CounterAPIValidationFactory.create_batch(3, core__user=normal_user)
        CounterAPIValidationFactory.create_batch(
            5, core__user=normal_user, core__expiration_date=now() - timedelta(hours=1)
        )
        res = client_authenticated_user.get(reverse("validation-list"))
        assert res.status_code == 200
        assert res.json()["count"] == 3

    @pytest.mark.parametrize("use_short_dates", [True, False])
    def test_create_with_short_dates(
        self, client_authenticated_user, requests_mock, settings, use_short_dates
    ):
        """
        Make sure that the `use_short_dates` parameter is reflected in the request to the API.
        """
        settings.VALIDATIO_MODULES_URLS = "http://localhost:8180/"
        data = factory.build(
            dict,
            FACTORY_CLASS=CounterAPIValidationRequestDataFactory,
            begin_date="2021-01-01",
            end_date="2021-01-31",
            use_short_dates=use_short_dates,
            url="https://foo.bar",
        )
        mock = requests_mock.post("http://localhost:8180/sushi.php", json={})
        with patch("validations.tasks.validate_counter_api.delay_on_commit") as p:
            res = client_authenticated_user.post(
                reverse("counter-api-validation-list"),
                data=data,
                format="json",
            )
            assert res.status_code == 201
            assert p.call_count == 1
            validation_id = res.json()["id"]
            # call the task manually to avoid the async part of the process
            validations.tasks.validate_counter_api(validation_id)
        # check params that were sent to the api through the mock
        assert mock.call_count == 1
        sent_url = mock.last_request.json()["url"]
        _scheme, _netloc, _path, query, _frag = urlsplit(sent_url)
        query_dict = parse_qs(query)
        assert query_dict["begin_date"] == (["2021-01"] if use_short_dates else ["2021-01-01"])
        assert query_dict["end_date"] == (["2021-01"] if use_short_dates else ["2021-01-31"])

    @pytest.mark.parametrize("missing_completely", [True, False])
    def test_create_with_no_credentials_required(
        self, client_authenticated_user, requests_mock, missing_completely
    ):
        data = factory.build(
            dict,
            FACTORY_CLASS=CounterAPIValidationRequestDataFactory,
            credentials=None,
            api_endpoint="/status",
            cop_version="5.1",
        )
        del data["begin_date"]
        del data["end_date"]
        if missing_completely:
            del data["credentials"]
        with patch("validations.tasks.validate_counter_api.delay_on_commit") as p:
            res = client_authenticated_user.post(
                reverse("counter-api-validation-list"),
                data=data,
                format="json",
            )
            assert res.status_code == 201
            p.assert_called_once_with(UUID(res.json()["id"]))
            rmock = requests_mock.post("http://localhost:8180/sushi.php", json={})
            validations.tasks.validate_counter_api(res.json()["id"])
            assert rmock.call_count == 1
            sent_url = rmock.last_request.json()["url"]
            _scheme, _netloc, _path, query, _frag = urlsplit(sent_url)
            query_dict = parse_qs(query)
            assert query_dict == {}, "no query parameters should be sent"

    @pytest.mark.parametrize(
        ["cop_version", "api_endpoint", "ok"],
        [
            ("5.1", "/status", True),
            ("5.1", "/reports/[id]", False),
            ("5", "/status", False),
            ("5", "/reports/[id]", False),
            ("5.2", "/status", True),
            ("5.2", "/reports/[id]", False),
        ],
    )
    def test_cases_with_no_credentials_required(
        self, client_authenticated_user, cop_version, api_endpoint, ok
    ):
        data = factory.build(
            dict,
            FACTORY_CLASS=CounterAPIValidationRequestDataFactory,
            credentials=None,
            api_endpoint=api_endpoint,
            cop_version=cop_version,
        )
        with patch("validations.tasks.validate_counter_api.delay_on_commit") as p:
            res = client_authenticated_user.post(
                reverse("counter-api-validation-list"),
                data=data,
                format="json",
            )
            assert res.status_code == 201 if ok else 400
            if ok:
                p.assert_called_once_with(UUID(res.json()["id"]))
            else:
                assert p.call_count == 0


@pytest.mark.django_db
class TestValidationMessagesAPI:
    def test_list(self, client_authenticated_user, normal_user):
        val = ValidationFactory(core__user=normal_user, messages__count=3)
        ValidationFactory(
            core__user=normal_user, messages__count=5
        )  # other validation, not in output
        res = client_authenticated_user.get(reverse("validation-message-list", args=[val.pk]))
        assert res.status_code == 200
        out = res.json()
        assert "count" in out, "count should be in the response - it should be paginated"
        assert "next" in out, "next should be in the response - it should be paginated"
        assert "previous" in out, "previous should be in the response - it should be paginated"
        assert "results" in out, "results should be in the response - it should be paginated"
        assert len(out["results"]) == 3
        first = out["results"][0]
        assert set(first.keys()) == {
            "code",
            "data",
            "hint",
            "location",
            "message",
            "severity",
            "summary",
        }

    def test_list_using_api_key(self, client_with_api_key, normal_user):
        val = ValidationFactory(core__user=normal_user, messages__count=3)
        res = client_with_api_key.get(reverse("validation-message-list", args=[val.pk]))
        assert res.status_code == 200
        out = res.json()
        assert len(out["results"]) == 3

    def test_detail(self, client_authenticated_user, normal_user):
        val = ValidationFactory(core__user=normal_user, messages__count=3)
        ValidationFactory(core__user=normal_user, messages__count=5)
        m = val.messages.first()
        res = client_authenticated_user.get(
            reverse("validation-message-detail", args=[val.pk, m.pk])
        )
        assert res.status_code == 200
        out = res.json()
        assert set(out.keys()) == {
            "code",
            "data",
            "hint",
            "location",
            "message",
            "severity",
            "summary",
        }

    @pytest.mark.parametrize("page_size", [5, 8, 10, 15])
    def test_list_pagination(self, client_authenticated_user, normal_user, page_size):
        val = ValidationFactory(core__user=normal_user, messages__count=10)
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
        val = ValidationFactory(core__user=normal_user, messages__count=10)
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
        val = ValidationFactory(core__user=normal_user, messages__count=10)
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
        val = ValidationFactory(core__user=normal_user)
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
    def test_list_is_forbidden(self, all_clients):
        res = all_clients.get(reverse("public-validation-list"))
        assert res.status_code == 403

    def test_detail(self, all_clients):
        """
        Detail of public validation should be accessible to any user - regardless of authentication.
        (provided he uses the correct public_id)
        """
        val = CounterAPIValidationFactory(public_id=uuid4())
        assert val.credentials is not None
        res = all_clients.get(reverse("public-validation-detail", args=[val.public_id]))
        assert res.status_code == 200
        out = res.json()
        assert set(out.keys()) == expected_validation_keys_detail - {
            "user"
        }, "user should not be there"
        assert out["credentials"] is None, "credentials should not be exposed"

    def test_detail_stats(self, all_clients):
        """
        Test that stats of a public validation are exposed even without authentication.

        The test was adapted from a similar test in `TestValidationAPI.test_validation_stats`.
        """
        val = CounterAPIValidationFactory(public_id=uuid4())
        ValidationMessageFactory.create(validation=val, severity=SeverityLevel.ERROR, summary="Aaa")
        ValidationMessageFactory.create_batch(
            2, validation=val, severity=SeverityLevel.NOTICE, summary="Bbb"
        )
        ValidationMessageFactory.create_batch(
            3, validation=val, severity=SeverityLevel.NOTICE, summary="Ccc"
        )

        res = all_clients.get(reverse("validation-stats", args=[val.public_id]))
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

    def test_detail_stats_not_publicly_available_using_pk(self, client_unauthenticated):
        val = CounterAPIValidationFactory(public_id=uuid4())
        res = client_unauthenticated.get(reverse("validation-stats", args=[val.pk]))
        assert res.status_code == 404

    def test_detail_messages(self, all_clients):
        """
        Test that messages of a public validation are exposed even without authentication.
        """
        val = CounterAPIValidationFactory(public_id=uuid4())
        ValidationMessageFactory.create_batch(3, validation=val, severity=SeverityLevel.ERROR)
        ValidationMessageFactory.create_batch(5, validation=val, severity=SeverityLevel.NOTICE)
        ValidationMessageFactory.create_batch(
            2, validation=val, severity=SeverityLevel.CRITICAL_ERROR
        )
        res = all_clients.get(reverse("validation-message-list", args=[val.public_id]))
        assert res.status_code == 200
        out = res.json()
        assert "results" in out
        assert len(out["results"]) == 10

    def test_detail_messages_not_publicly_available_using_pk(self, client_unauthenticated):
        val = CounterAPIValidationFactory(public_id=uuid4())
        res = client_unauthenticated.get(reverse("validation-message-list", args=[val.pk]))
        assert res.status_code == 403


@pytest.mark.django_db
class TestValidationAPIThrottling:
    def test_list_get_with_api_key(self, client_with_api_key, normal_user, settings):
        """
        Test that GET requests are not throttled.
        """
        settings.REST_FRAMEWORK["DEFAULT_THROTTLE_RATES"]["api_keys"] = "1/minute"
        ValidationFactory.create_batch(10, core__user=normal_user)
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
        ValidationFactory.create_batch(10, core__user=normal_user)
        res = client_authenticated_user.get(reverse("validation-list"))
        assert res.status_code == 200
        assert res.json()["count"] == 10
        # second request should not be throttled
        res = client_authenticated_user.get(reverse("validation-list"))
        assert res.status_code == 200
        assert res.json()["count"] == 10
