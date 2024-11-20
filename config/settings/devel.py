from .base import *  # noqa F403

ALLOWED_HOSTS = ["*"]

CSRF_TRUSTED_ORIGINS = ["http://localhost:3030"]

# debug toolbar
INSTALLED_APPS += ("debug_toolbar",)  # noqa F405
MIDDLEWARE = (
    MIDDLEWARE[:-1]  # noqa F405
    + ("debug_toolbar.middleware.DebugToolbarMiddleware",)
    + MIDDLEWARE[-1:]  # noqa F405
    + ("core.middleware.DebugSleepMiddleware",)
)
INTERNAL_IPS = ["127.0.0.1"]

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
