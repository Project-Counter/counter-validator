from urllib.parse import urlparse

import requests
import tomllib
from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.core.cache import cache

UPSTREAM_SERVER = "https://validator.bigdigdata.com/"
UPSTREAM_VERSION_CACHE_KEY = "upstream_version"
UPSTREAM_VERSION_CACHE_TTL = 3600
VERSION_INFO_PATH = "/api/v1/core/version"


def get_server_version() -> str:
    try:
        with (settings.BASE_DIR / "pyproject.toml").open("rb") as f:
            data = tomllib.load(f)
            try:
                return data["tool"]["poetry"]["version"]
            except KeyError:
                raise RuntimeError("Version not found in pyproject.toml") from None

    except Exception as e:
        raise RuntimeError("Failed to read pyproject.toml") from e


def get_upstream_version_lowlevel() -> str:
    response = requests.get(
        f"{UPSTREAM_SERVER.rstrip('/')}{VERSION_INFO_PATH}",
        {"our-version": get_server_version()},
        timeout=5,
    )
    if response.status_code != 200:
        raise RuntimeError(f"Failed to get upstream version: {response.status_code}")
    return response.json()["server"]


def get_upstream_version() -> str:
    site = get_current_site(None)
    url = urlparse(UPSTREAM_SERVER)
    if site.domain == url.netloc:
        # we are the upstream server
        return get_server_version()
    if upstream_version := cache.get(UPSTREAM_VERSION_CACHE_KEY):
        return upstream_version
    upstream_version = get_upstream_version_lowlevel()
    cache.set(UPSTREAM_VERSION_CACHE_KEY, upstream_version, UPSTREAM_VERSION_CACHE_TTL)
    return upstream_version
