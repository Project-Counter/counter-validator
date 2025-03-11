import pytest
from django.urls import reverse


@pytest.mark.django_db
class TestCeleryAPI:
    def test_validation_queue_info(self, admin_client):
        url = reverse("validation-queue-info")
        assert url == "/api/v1/validations/queue/"
        response = admin_client.get(url)
        assert response.status_code == 200
        assert response.json() == {"queued": 0, "running": 0, "workers": 1}
