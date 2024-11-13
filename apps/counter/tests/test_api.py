import pytest
from django.urls import reverse

from counter.fake_data import PlatformFactory


@pytest.mark.django_db
class TestPlatformAPI:
    def test_platform_list(self, client_authenticated_user, django_assert_max_num_queries):
        PlatformFactory.create_batch(10)
        with django_assert_max_num_queries(9):
            res = client_authenticated_user.get(reverse("platform-list"))
        assert res.status_code == 200
        assert len(res.json()) == 10
        first = res.json()[0]
        assert "name" in first
        assert "abbrev" in first
        assert "id" in first
        assert "deprecated" in first

    def test_platform_detail(self, client_authenticated_user):
        platform = PlatformFactory()
        res = client_authenticated_user.get(reverse("platform-detail", kwargs={"pk": platform.pk}))
        assert res.status_code == 200
        assert res.json()["name"] == platform.name
        data = res.json()
        assert "name" in data
        assert "abbrev" in data
        assert "id" in data
        assert "deprecated" in data

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
