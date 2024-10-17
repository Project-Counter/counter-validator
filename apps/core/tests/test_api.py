"""
General API tests. Specific API tests may be in other files.
"""

import pytest
from django.urls import reverse

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
