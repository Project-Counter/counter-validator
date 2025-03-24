import pytest
from django.urls import reverse


@pytest.mark.django_db
class TestCeleryAPI:
    @pytest.mark.parametrize(
        ["validation_modules_urls", "expected_workers"],
        [
            (["https://example.com"], 1),
            (["https://example.com", "https://example2.com"], 2),
        ],
    )
    def test_validation_queue_info(
        self, admin_client, settings, validation_modules_urls, expected_workers
    ):
        settings.VALIDATION_MODULES_URLS = validation_modules_urls
        url = reverse("validation-queue-info")
        assert url == "/api/v1/validations/queue/"
        response = admin_client.get(url)
        assert response.status_code == 200
        assert response.json() == {"queued": 0, "running": 0, "workers": expected_workers}

    @pytest.mark.parametrize(
        ["user_type", "can_access"],
        [
            ("unauthenticated", False),
            ("normal", False),
            ("su", True),
            ("admin", True),
            ("api_key_normal", False),
        ],
    )
    def test_validation_queue_info_access(self, users_and_clients, user_type, can_access):
        _user, client = users_and_clients[user_type]
        res = client.get(reverse("validation-queue-info"))
        assert res.status_code == (200 if can_access else 403)
