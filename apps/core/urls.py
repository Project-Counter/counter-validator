from rest_framework.routers import SimpleRouter

from . import views

router = SimpleRouter()
router.register(r"validation", views.ValidationViewSet, basename="validation")
router.register(r"api-key", views.UserApiKeyViewSet, basename="api-key")
router.register(r"platform", views.PlatformViewSet, basename="platform")


urlpatterns = router.urls
