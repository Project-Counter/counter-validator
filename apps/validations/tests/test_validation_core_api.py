import pytest
from django.urls import reverse

from validations.enums import SeverityLevel
from validations.fake_data import ValidationCoreFactory


@pytest.mark.django_db
class TestValidationCoreAPI:
    def test_access(self, client):
        res = client.get(reverse("validation-core-list"))
        assert res.status_code == 403

    def test_access_admin(self, admin_client):
        res = admin_client.get(reverse("validation-core-list"))
        assert res.status_code == 200

    @pytest.mark.parametrize("page_size", [5, 10, 20])
    def test_list(self, admin_client, django_assert_max_num_queries, page_size):
        ValidationCoreFactory.create_batch(10)
        with django_assert_max_num_queries(9):
            res = admin_client.get(reverse("validation-core-list"), {"page_size": page_size})
            assert res.status_code == 200
            assert res.json()["count"] == 10
            assert "next" in res.json()
            data = res.json()["results"]
            assert len(data) == min(page_size, 10)
            first = data[0]
            # check fields that should be there
            assert "id" in first
            assert "status" in first
            assert "platform" in first
            assert "platform_name" in first
            assert "validation_result" in first
            assert "created" in first
            assert "cop_version" in first
            assert "report_code" in first
            assert "file_size" in first
            assert "used_memory" in first
            assert "duration" in first
            assert "stats" in first
            assert "error_message" in first
            assert "source" in first and first["source"] == "file"
            # stuff that should not be there - it is in Validation only
            assert "filename" not in first
            assert "result_data" not in first

    @pytest.mark.parametrize(
        ["query", "expected_count"], [["5", 1], ["5,5.1", 3], ["5.1", 2], ["", 3]]
    )
    def test_list_filters_cop_version(self, admin_client, query, expected_count):
        ValidationCoreFactory.create_batch(1, cop_version="5")
        ValidationCoreFactory.create_batch(2, cop_version="5.1")
        res = admin_client.get(reverse("validation-core-list"), {"cop_version": query})
        assert res.status_code == 200
        assert res.json()["count"] == expected_count

    def test_list_filters_validation_result(self, admin_client):
        ValidationCoreFactory.create_batch(3, validation_result=SeverityLevel.NOTICE)
        ValidationCoreFactory.create_batch(5, validation_result=SeverityLevel.ERROR)

        res = admin_client.get(
            reverse("validation-core-list"), {"validation_result": SeverityLevel.NOTICE.label}
        )
        assert res.status_code == 200
        assert res.json()["count"] == 3
        # test with multiple values
        res = admin_client.get(
            reverse("validation-core-list"),
            {"validation_result": f"{SeverityLevel.ERROR.label},{SeverityLevel.NOTICE.label}"},
        )
        assert res.status_code == 200
        assert res.json()["count"] == 8

    @pytest.mark.parametrize(
        ["query", "expected_count"], [["TR", 1], ["TR,DR", 3], ["", 3], ["DR", 2]]
    )
    def test_list_filters_by_report_code(self, admin_client, query, expected_count):
        ValidationCoreFactory.create_batch(1, report_code="TR")
        ValidationCoreFactory.create_batch(2, report_code="DR")
        res = admin_client.get(reverse("validation-core-list"), {"report_code": query})
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
    def test_list_filters_by_api_endpoint(self, admin_client, query, expected_count):
        ValidationCoreFactory.create_batch(1, api_endpoint="/members")
        ValidationCoreFactory.create_batch(2, api_endpoint="/status")
        ValidationCoreFactory.create_batch(3, api_endpoint="/reports/[id]")
        res = admin_client.get(reverse("validation-core-list"), {"api_endpoint": query})
        assert res.status_code == 200
        assert res.json()["count"] == expected_count

    @pytest.mark.parametrize(
        ["query", "expected_count"],
        [["file", 1], ["counter_api", 2], ["", 3], ["file,counter_api", 3]],
    )
    def test_list_filters_by_data_source(self, admin_client, query, expected_count):
        ValidationCoreFactory.create_batch(1)
        ValidationCoreFactory.create_batch(2, sushi_credentials_checksum="123")
        res = admin_client.get(reverse("validation-core-list"), {"data_source": query})
        assert res.status_code == 200
        assert res.json()["count"] == expected_count

    @pytest.mark.parametrize("desc", [True, False])
    @pytest.mark.parametrize(
        "attr",
        [
            "cop_version",
            "created",
            "file_size",
            "platform_name",
            "report_code",
            "status",
            "validation_result",
        ],
    )
    def test_list_filters_order_by_filesize(self, admin_client, desc, attr):
        ValidationCoreFactory.create_batch(3)
        res = admin_client.get(
            reverse("validation-core-list"), {"order_by": attr, "order_desc": desc}
        )
        assert res.status_code == 200
        assert res.json()["count"] == 3
        if desc:
            assert res.json()["results"][0][attr] >= res.json()["results"][-1][attr]
        else:
            assert res.json()["results"][0][attr] <= res.json()["results"][-1][attr]

    def test_delete_not_allowed(self, admin_client):
        v = ValidationCoreFactory()
        res = admin_client.delete(reverse("validation-core-detail", args=[v.pk]))
        assert res.status_code == 405

    def test_stats(self, admin_client, django_assert_max_num_queries):
        ValidationCoreFactory.create_batch(10)
        with django_assert_max_num_queries(9):
            res = admin_client.get(reverse("validation-core-stats"))
            assert res.status_code == 200
            data = res.json()
            assert "total" in data
            for key in ["duration", "file_size", "used_memory"]:
                assert key in data
                assert "min" in data[key]
                assert "max" in data[key]
                assert "avg" in data[key]
                assert "median" in data[key]

    def test_time_stats(self, admin_client, django_assert_max_num_queries):
        ValidationCoreFactory.create_batch(10)
        with django_assert_max_num_queries(9):
            res = admin_client.get(reverse("validation-core-time-stats"))
            assert res.status_code == 200
            data = res.json()
            assert len(data) == 1, "just today"
            assert "total" in data[0]
            assert data[0]["total"] == 10
            assert "date" in data[0]
            for severity in SeverityLevel:
                if severity.label:
                    assert severity.label in data[0]

    def test_split_stats(self, admin_client, django_assert_max_num_queries):
        ValidationCoreFactory.create_batch(10)
        with django_assert_max_num_queries(9):
            res = admin_client.get(reverse("validation-core-split-stats"))
            assert res.status_code == 200
            data = res.json()
            first = data[0]
            assert "result" in first
            assert "source" in first
            assert "method" in first
            assert "cop_version" in first
            assert "report_code" in first
            assert "count" in first
