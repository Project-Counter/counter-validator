from datetime import datetime, timedelta

import pytest
from core.fake_data import UserFactory
from django.urls import reverse
from django.utils.timezone import make_aware, timezone

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

    @pytest.mark.parametrize(
        ["filter_date", "timezone_name", "expected_count", "description"],
        [
            (
                "2024-01-15",
                "Asia/Jerusalem",
                1,
                "Filter by same date in Asia/Jerusalem timezone (UTC+2/UTC+3)",
            ),
            (
                "2024-01-15",
                "UTC",
                1,
                "Filter by same date in UTC timezone - should match (validation is at 23:59 UTC+3 "
                "= 20:59 UTC, so it's on 2024-01-15 in both UTC+3 and UTC)",
            ),
            (
                "2024-01-15",
                "America/New_York",
                1,
                "Filter by same date in America/New_York timezone (UTC-5/UTC-4) - should match "
                "(validation is at 20:59 UTC, which is 15:59 EST, so it's on 2024-01-15 in EST)",
            ),
            (
                "2024-01-16",
                "UTC",
                0,
                "Filter by next day in UTC timezone - should not match (validation at 20:59 UTC "
                "on 2024-01-15, so it's not on 2024-01-16 in UTC)",
            ),
            (
                "2024-01-16",
                "Asia/Jerusalem",
                0,
                "Filter by next day in Asia/Jerusalem timezone - should not match",
            ),
            (
                "2024-01-14",
                "Asia/Jerusalem",
                0,
                "Filter by previous day in Asia/Jerusalem timezone - should not match",
            ),
            (
                "",
                "Asia/Jerusalem",
                1,
                "No date filter with timezone - should return all validations",
            ),
            (
                "invalid-date",
                "Asia/Jerusalem",
                1,
                "Invalid date format with timezone - should return all validations",
            ),
        ],
    )
    def test_list_filters_by_date_with_timezone_awareness(
        self,
        client_su_user,
        filter_date,
        timezone_name,
        expected_count,
        description,
    ):
        """
        Test that date filtering works correctly with timezone-aware datetime fields for
        ValidationCore.

        Creates a validation core at 2024-01-15 23:59:59 UTC+3 and tests filtering
        with different dates and timezones to ensure timezone handling works correctly.

        The validation core is created at:
        - 2024-01-15 23:59:59 UTC+3
        - 2024-01-15 20:59:59 UTC
        - 2024-01-15 15:59:59 EST (America/New_York)
        """
        # Create a validation core at a specific time on 2024-01-15 in UTC+3 timezone
        # This is 2024-01-15 20:59:59 UTC (3 hours behind)
        utc_plus_3 = timezone(timedelta(hours=3))
        target_datetime = datetime(2024, 1, 15, 23, 59, 59)
        target_date_utc_plus_3 = make_aware(target_datetime, timezone=utc_plus_3)

        validation_core = ValidationCoreFactory()
        validation_core.created = target_date_utc_plus_3
        validation_core.save()

        # Filter by the specified date and timezone
        query_params = {}
        if filter_date:
            query_params["date"] = filter_date
        if timezone_name:
            query_params["timezone"] = timezone_name

        res = client_su_user.get(reverse("validation-core-list"), query_params)
        assert res.status_code == 200
        assert res.json()["count"] == expected_count, f"Failed: {description}"

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


@pytest.mark.django_db
class TestValidationCoreStats:
    def test_stats(self, client_su_user, django_assert_max_num_queries):
        ValidationCoreFactory.create_batch(10)
        with django_assert_max_num_queries(9):
            res = client_su_user.get(reverse("validation-core-stats"))
            assert res.status_code == 200
            data = res.json()
            assert "total" in data
            assert data["total"] == 10
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

    def test_stats_with_user_filter(self, client_su_user):
        u1 = UserFactory()
        u2 = UserFactory()
        ValidationCoreFactory.create_batch(2, user=u1, file_size=100)
        ValidationCoreFactory.create_batch(3, user=u2, file_size=200)
        res = client_su_user.get(reverse("validation-core-stats"), {"user": u1.pk})
        assert res.status_code == 200
        data = res.json()
        assert data["total"] == 2
        assert data["file_size"]["min"] == 100
        assert data["file_size"]["max"] == 100
        assert data["file_size"]["avg"] == 100
        assert data["file_size"]["median"] == 100

    def test_stats_with_user_filter_not_found(self, client_su_user):
        res = client_su_user.get(reverse("validation-core-stats"), {"user": 0})
        assert res.status_code == 404

    def test_time_stats_with_user_filter(self, client_su_user):
        u1 = UserFactory()
        u2 = UserFactory()
        ValidationCoreFactory.create_batch(2, user=u1)
        ValidationCoreFactory.create_batch(3, user=u2)
        res = client_su_user.get(reverse("validation-core-time-stats"), {"user": u1.pk})
        assert res.status_code == 200
        data = res.json()
        assert len(data) == 1, "just today"
        assert "total" in data[0]
        assert data[0]["total"] == 2

    def test_time_stats_with_user_filter_not_found(self, client_su_user):
        res = client_su_user.get(reverse("validation-core-time-stats"), {"user": 0})
        assert res.status_code == 404

    def test_split_stats_with_user_filter(self, client_su_user):
        u1 = UserFactory()
        u2 = UserFactory()
        ValidationCoreFactory.create_batch(2, user=u1, validation_result=SeverityLevel.NOTICE)
        ValidationCoreFactory.create_batch(3, user=u2, validation_result=SeverityLevel.ERROR)
        res = client_su_user.get(reverse("validation-core-split-stats"), {"user": u1.pk})
        assert res.status_code == 200
        data = res.json()
        assert len(data) == 1
        assert data[0]["count"] == 2
        assert data[0]["result"] == "Notice"

    def test_split_stats_with_user_filter_not_found(self, client_su_user):
        res = client_su_user.get(reverse("validation-core-split-stats"), {"user": 0})
        assert res.status_code == 404
