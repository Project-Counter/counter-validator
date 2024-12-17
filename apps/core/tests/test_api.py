"""
General API tests. Specific API tests may be in other files.
"""

import pytest
from django.urls import reverse

from ..models import UserApiKey


@pytest.mark.django_db
class TestApi:
    def test_user_detail_access(self, client_and_status_code_any_authenticated):
        client, status_code = client_and_status_code_any_authenticated
        res = client.get(reverse("user-detail"))
        assert res.status_code == status_code

    def test_user_detail(self, client_authenticated_user, normal_user):
        res = client_authenticated_user.get(reverse("user-detail"))
        assert res.status_code == 200, "user should see his details"
        assert res.data["id"] == normal_user.id
        assert res.json()["email"] == normal_user.email
        assert res.json()["first_name"] == normal_user.first_name
        assert res.json()["last_name"] == normal_user.last_name
        assert res.json()["is_validator_admin"] == normal_user.is_validator_admin
        assert res.json()["is_superuser"] == normal_user.is_superuser


@pytest.mark.django_db
class TestApiKeyAPI:
    def test_api_key_list(
        self, client_authenticated_user, django_assert_max_num_queries, normal_user
    ):
        for i in range(10):
            UserApiKey.objects.create_key(name=f"key-{i}", user=normal_user)
        with django_assert_max_num_queries(9):
            print(reverse("api-key-list"))
            res = client_authenticated_user.get(reverse("api-key-list"))
            assert res.status_code == 200
            assert len(res.json()) == 10

    def test_api_key_detail(self, client_authenticated_user, normal_user):
        api_key, key = UserApiKey.objects.create_key(name="foo", user=normal_user)
        res = client_authenticated_user.get(
            reverse("api-key-detail", kwargs={"prefix": api_key.prefix})
        )
        assert res.status_code == 200
        assert res.json()["name"] == "foo"

    def test_api_key_create(self, client_authenticated_user):
        res = client_authenticated_user.post(reverse("api-key-list"), data={"name": "foo"})
        assert res.status_code == 201
        assert "key" in res.json()

    def test_api_key_revoke(self, client_authenticated_user, normal_user):
        api_key, key = UserApiKey.objects.create_key(name="foo", user=normal_user)
        res = client_authenticated_user.delete(
            reverse("api-key-detail", kwargs={"prefix": api_key.prefix})
        )
        assert res.status_code == 200
        assert UserApiKey.objects.get(prefix=api_key.prefix).revoked
