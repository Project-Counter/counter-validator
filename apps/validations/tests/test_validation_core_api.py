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

    def test_list(self, admin_client, django_assert_max_num_queries):
        ValidationCoreFactory.create_batch(10)
        with django_assert_max_num_queries(9):
            res = admin_client.get(reverse("validation-core-list"))
            assert res.status_code == 200
            assert len(res.json()) == 10
            first = res.json()[0]
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
            assert "count" in first
