"""
General API tests. Specific API tests may be in other files.
"""

import pytest
from django.urls import reverse

from ..models import UserApiKey
from ..urls import urlpatterns


@pytest.mark.django_db
class TestApi:
    urls = set(path.name for path in urlpatterns)
    urls_kwargs = {
        "validation-detail": {
            "pk": 1,
        },
        "validation-details": {
            "pk": 1,
        },
        "platform-detail": {
            "pk": "uuid-",
        },
        "sushi-detail": {
            "pk": "uuid-",
        },
        "api-key-detail": {
            "prefix": "6mxB2Ads",
        },
        "validation-file": {
            "filename": "tr.json",
        },
    }
    public_urls = set()
    admin_urls = set()

    @pytest.mark.parametrize("url", urls - public_urls)
    def test_auth_only(self, url, client_unauthenticated):
        res = client_unauthenticated.get(reverse(url, kwargs=self.urls_kwargs.get(url, {})))
        assert res.status_code in (
            401,
            403,
        ), "url requiring auth shouldn't be public"  # support different auth

    @pytest.mark.parametrize("url", admin_urls)
    def test_admin_only(self, url, client_authenticated_user):
        res = client_authenticated_user.get(reverse(url, kwargs=self.urls_kwargs.get(url, {})))
        assert res.status_code in (
            401,
            403,
        ), "admin only url shouldn't be public"  # support different auth


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
