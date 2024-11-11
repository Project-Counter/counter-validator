import pytest
from django.urls import reverse

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
            # stuff that should not be there - it is in Validation only
            assert "filename" not in first
            assert "result_data" not in first

    def test_delete_not_allowed(self, admin_client):
        v = ValidationCoreFactory()
        res = admin_client.delete(reverse("validation-core-detail", args=[v.pk]))
        assert res.status_code == 405
