from .base import *  # noqa F403

ALLOWED_HOSTS = ("*",)

# debug toolbar
INSTALLED_APPS += ("debug_toolbar",)  # noqa F405
MIDDLEWARE = (
    MIDDLEWARE[:-1]  # noqa F405
    + ("debug_toolbar.middleware.DebugToolbarMiddleware",)
    + MIDDLEWARE[-1:]  # noqa F405
)
INTERNAL_IPS = ["127.0.0.1"]
