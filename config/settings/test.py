from .base import *  # noqa F403

STORAGES = {
    "default": {"BACKEND": "inmemorystorage.InMemoryStorage"},
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
}
