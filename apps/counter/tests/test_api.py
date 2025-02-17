import pytest
from django.urls import reverse

from counter.fake_data import PlatformFactory, SushiServiceFactory


@pytest.mark.django_db
class TestPlatformAPI:
    def test_platform_list(self, client_authenticated_user, django_assert_max_num_queries):
        PlatformFactory.create_batch(10)
        with django_assert_max_num_queries(9):
            res = client_authenticated_user.get(reverse("platform-list"))
        assert res.status_code == 200
        assert len(res.json()) == 10
        first = res.json()[0]
        assert set(first.keys()) == {"name", "abbrev", "id", "deprecated"}

    def test_platform_detail(self, client_authenticated_user):
        platform = PlatformFactory()
        SushiServiceFactory(platform=platform)
        res = client_authenticated_user.get(reverse("platform-detail", kwargs={"pk": platform.pk}))
        assert res.status_code == 200
        assert res.json()["name"] == platform.name
        data = res.json()
        assert set(data.keys()) == {
            "name",
            "abbrev",
            "id",
            "deprecated",
            "reports",
            "sushi_services",
            "website",
            "content_provider_name",
        }
        assert type(data["reports"]) is list
        assert type(data["sushi_services"]) is list
        assert type(data["sushi_services"][0]) is dict

    def test_platform_create(self, client_authenticated_user):
        """
        Creating of platforms through the API should not be possible.
        """
        res = client_authenticated_user.post(reverse("platform-list"), data={"name": "foo"})
        assert res.status_code == 405
        assert "detail" in res.json()
        assert res.json()["detail"] == 'Method "POST" not allowed.'

    def test_platform_update(self, client_authenticated_user):
        """
        Updating of platforms through the API should not be possible.
        """
        platform = PlatformFactory()
        res = client_authenticated_user.put(
            reverse("platform-detail", kwargs={"pk": platform.pk}), data={"name": "foo"}
        )
        assert res.status_code == 405
        assert "detail" in res.json()
        assert res.json()["detail"] == 'Method "PUT" not allowed.'

    def test_platform_delete(self, client_authenticated_user):
        """
        Deleting of platforms through the API should not be possible.
        """
        platform = PlatformFactory()
        res = client_authenticated_user.delete(
            reverse("platform-detail", kwargs={"pk": platform.pk})
        )
        assert res.status_code == 405
        assert "detail" in res.json()
        assert res.json()["detail"] == 'Method "DELETE" not allowed.'
