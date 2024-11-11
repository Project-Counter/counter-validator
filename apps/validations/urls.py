from rest_framework.routers import SimpleRouter

from . import views

router = SimpleRouter()
router.register(r"validation", views.ValidationViewSet, basename="validation")
router.register(r"validation-core", views.ValidationCoreViewSet, basename="validation-core")

urlpatterns = router.urls
