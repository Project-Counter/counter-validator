import re
from unittest.mock import patch

import pytest
from django.contrib.sites.models import Site

from core.version import (
    UPSTREAM_SERVER,
    UPSTREAM_VERSION_CACHE_KEY,
    UPSTREAM_VERSION_CACHE_TTL,
    VERSION_INFO_PATH,
    get_server_version,
    get_upstream_version,
    get_upstream_version_lowlevel,
)


@pytest.mark.django_db
class TestVersion:
    def test_server_version(self):
        assert re.match(r"\d+\.\d+\.\d+", get_server_version())

    def test_upstream_version_lowlevel(self, requests_mock):
        mock = requests_mock.get(
            f"{UPSTREAM_SERVER}{VERSION_INFO_PATH.lstrip('/')}", json={"server": "1.2.3"}
        )
        assert get_upstream_version_lowlevel() == "1.2.3"
        assert mock.call_count == 1

    @pytest.mark.parametrize("status_code", [400, 404, 429, 500])
    def test_upstream_version_lowlevel_error(self, requests_mock, status_code):
        mock = requests_mock.get(
            f"{UPSTREAM_SERVER}{VERSION_INFO_PATH.lstrip('/')}", status_code=status_code
        )
        with pytest.raises(RuntimeError):
            get_upstream_version_lowlevel()
        assert mock.call_count == 1

    def test_upstream_version_with_caching(self, requests_mock):
        rmock = requests_mock.get(
            f"{UPSTREAM_SERVER}{VERSION_INFO_PATH.lstrip('/')}", json={"server": "1.2.3"}
        )
        with patch("core.version.cache") as cache:
            cache.get.return_value = None
            assert get_upstream_version() == "1.2.3"
            assert cache.get.call_count == 1
            assert cache.set.call_count == 1
            cache.set.assert_called_with(
                UPSTREAM_VERSION_CACHE_KEY, "1.2.3", UPSTREAM_VERSION_CACHE_TTL
            )
            assert rmock.call_count == 1

    def test_upstream_version_with_caching_cached(self, requests_mock):
        mock = requests_mock.get(
            f"{UPSTREAM_SERVER}{VERSION_INFO_PATH.lstrip('/')}", json={"server": "1.2.3"}
        )
        with patch("core.version.cache") as cache:
            cache.get.return_value = "3.2.1"
            assert get_upstream_version() == "3.2.1"
            assert mock.call_count == 0
            assert cache.get.call_count == 1
            assert cache.set.call_count == 0

    def test_with_site_equal_to_upstream(self, requests_mock, settings):
        site = Site.objects.get(pk=settings.SITE_ID)
        site.domain = UPSTREAM_SERVER.removeprefix("https://").removesuffix("/")
        site.save()

        mock = requests_mock.get(
            f"{UPSTREAM_SERVER}{VERSION_INFO_PATH.lstrip('/')}", json={"server": "1.2.3"}
        )
        with (
            patch("core.version.cache") as cache,
            patch("core.version.get_server_version") as sv_mock,
        ):
            sv_mock.return_value = "5.6.7"
            cache.get.return_value = "3.2.1"
            assert get_upstream_version() == "5.6.7", "the same as our server version"
            assert mock.call_count == 0
            assert cache.get.call_count == 0
            assert cache.set.call_count == 0
