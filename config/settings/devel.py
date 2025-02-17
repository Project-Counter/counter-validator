from .base import *  # noqa F403

ALLOWED_HOSTS = ["*"]

CSRF_TRUSTED_ORIGINS = ["http://localhost:3030"]

# debug toolbar
USE_SILK = config("USE_SILK", cast=bool, default=False)  # noqa F405, config comes from .base

INSTALLED_APPS += ("debug_toolbar",)  # noqa F405
if USE_SILK:
    INSTALLED_APPS += ("silk",)  # noqa F405

prepend_middlewares = [
    "debug_toolbar.middleware.DebugToolbarMiddleware",
]
if USE_SILK:
    prepend_middlewares.append("silk.middleware.SilkyMiddleware")

MIDDLEWARE = (
    MIDDLEWARE[:-1]  # noqa F405
    + tuple(prepend_middlewares)
    + MIDDLEWARE[-1:]  # noqa F405
    + ("core.middleware.DebugSleepMiddleware",)
)
INTERNAL_IPS = ["127.0.0.1"]

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
