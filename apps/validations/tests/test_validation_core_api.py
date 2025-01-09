import pytest
from core.fake_data import UserFactory
from django.urls import reverse

from validations.enums import SeverityLevel
from validations.fake_data import ValidationCoreFactory


@pytest.mark.django_db
class TestValidationCoreAPI:
    def test_access(self, client_and_status_code_admin_only):
        client, status_code = client_and_status_code_admin_only
        res = client.get(reverse("validation-core-list"))
        assert res.status_code == status_code

    @pytest.mark.parametrize("page_size", [5, 10, 20])
    def test_list(self, client_su_user, django_assert_max_num_queries, page_size):
        ValidationCoreFactory.create_batch(10)
        with django_assert_max_num_queries(9):
            res = client_su_user.get(reverse("validation-core-list"), {"page_size": page_size})
            assert res.status_code == 200
            assert res.json()["count"] == 10
            assert "next" in res.json()
            data = res.json()["results"]
            assert len(data) == min(page_size, 10)
            first = data[0]
            # check fields that should be there
            assert set(first.keys()) == {
                "cop_version",
                "created",
                "duration",
                "error_message",
                "file_size",
                "id",
                "report_code",
                "source",
                "stats",
                "status",
                "used_memory",
                "user",
                "validation_result",
            }
            # check content values
            assert first["source"] == "file"

    @pytest.mark.parametrize(
        ["query", "expected_count"], [["5", 1], ["5,5.1", 3], ["5.1", 2], ["", 3]]
    )
    def test_list_filters_cop_version(self, client_su_user, query, expected_count):
        ValidationCoreFactory.create_batch(1, cop_version="5")
        ValidationCoreFactory.create_batch(2, cop_version="5.1")
        res = client_su_user.get(reverse("validation-core-list"), {"cop_version": query})
        assert res.status_code == 200
        assert res.json()["count"] == expected_count

    def test_list_filters_validation_result(self, client_su_user):
        ValidationCoreFactory.create_batch(3, validation_result=SeverityLevel.NOTICE)
        ValidationCoreFactory.create_batch(5, validation_result=SeverityLevel.ERROR)

        res = client_su_user.get(
            reverse("validation-core-list"), {"validation_result": SeverityLevel.NOTICE.label}
        )
        assert res.status_code == 200
        assert res.json()["count"] == 3
        # test with multiple values
        res = client_su_user.get(
            reverse("validation-core-list"),
            {"validation_result": f"{SeverityLevel.ERROR.label},{SeverityLevel.NOTICE.label}"},
        )
        assert res.status_code == 200
        assert res.json()["count"] == 8

    @pytest.mark.parametrize(
        ["query", "expected_count"], [["TR", 1], ["TR,DR", 3], ["", 3], ["DR", 2]]
    )
    def test_list_filters_by_report_code(self, client_su_user, query, expected_count):
        ValidationCoreFactory.create_batch(1, report_code="TR")
        ValidationCoreFactory.create_batch(2, report_code="DR")
        res = client_su_user.get(reverse("validation-core-list"), {"report_code": query})
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
    def test_list_filters_by_api_endpoint(self, client_su_user, query, expected_count):
        ValidationCoreFactory.create_batch(1, api_endpoint="/members")
        ValidationCoreFactory.create_batch(2, api_endpoint="/status")
        ValidationCoreFactory.create_batch(3, api_endpoint="/reports/[id]")
        res = client_su_user.get(reverse("validation-core-list"), {"api_endpoint": query})
        assert res.status_code == 200
        assert res.json()["count"] == expected_count

    @pytest.mark.parametrize(
        ["query", "expected_count"],
        [["file", 1], ["counter_api", 2], ["", 3], ["file,counter_api", 3]],
    )
    def test_list_filters_by_data_source(self, client_su_user, query, expected_count):
        ValidationCoreFactory.create_batch(1)
        ValidationCoreFactory.create_batch(2, sushi_credentials_checksum="123")
        res = client_su_user.get(reverse("validation-core-list"), {"data_source": query})
        assert res.status_code == 200
        assert res.json()["count"] == expected_count

    def test_list_filter_by_text(self, client_su_user):
        u1 = UserFactory(email="foo@bar.baz")
        u2 = UserFactory(email="bar@baz.com")
        ValidationCoreFactory.create_batch(2, user=u1)
        ValidationCoreFactory.create_batch(3, user=u2)
        res = client_su_user.get(reverse("validation-core-list"), {"search": "foo"})
        assert res.status_code == 200
        assert res.json()["count"] == 2

    @pytest.mark.parametrize("desc", [True, False])
    @pytest.mark.parametrize(
        "attr",
        [
            "cop_version",
            "created",
            "file_size",
            "report_code",
            "status",
            "validation_result",
        ],
    )
    def test_list_filters_order_by_filesize(self, client_su_user, desc, attr):
        ValidationCoreFactory.create_batch(3)
        res = client_su_user.get(
            reverse("validation-core-list"), {"order_by": attr, "order_desc": desc}
        )
        assert res.status_code == 200
        assert res.json()["count"] == 3
        if desc:
            assert res.json()["results"][0][attr] >= res.json()["results"][-1][attr]
        else:
            assert res.json()["results"][0][attr] <= res.json()["results"][-1][attr]

    def test_delete_not_allowed(self, client_su_user):
        v = ValidationCoreFactory()
        res = client_su_user.delete(reverse("validation-core-detail", args=[v.pk]))
        assert res.status_code == 405

    def test_stats(self, client_su_user, django_assert_max_num_queries):
        ValidationCoreFactory.create_batch(10)
        with django_assert_max_num_queries(9):
            res = client_su_user.get(reverse("validation-core-stats"))
            assert res.status_code == 200
            data = res.json()
            assert "total" in data
            for key in ["duration", "file_size", "used_memory"]:
                assert key in data
                assert "min" in data[key]
                assert "max" in data[key]
                assert "avg" in data[key]
                assert "median" in data[key]

    def test_time_stats(self, client_su_user, django_assert_max_num_queries):
        ValidationCoreFactory.create_batch(10)
        with django_assert_max_num_queries(9):
            res = client_su_user.get(reverse("validation-core-time-stats"))
            assert res.status_code == 200
            data = res.json()
            assert len(data) == 1, "just today"
            assert "total" in data[0]
            assert data[0]["total"] == 10
            assert "date" in data[0]
            for severity in SeverityLevel:
                if severity.label:
                    assert severity.label in data[0]

    def test_split_stats(self, client_su_user, django_assert_max_num_queries):
        ValidationCoreFactory.create_batch(10)
        with django_assert_max_num_queries(9):
            res = client_su_user.get(reverse("validation-core-split-stats"))
            assert res.status_code == 200
            data = res.json()
            first = data[0]
            assert set(first.keys()) == {
                "result",
                "source",
                "method",
                "cop_version",
                "report_code",
                "count",
            }
