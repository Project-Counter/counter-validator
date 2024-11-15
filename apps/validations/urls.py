from rest_framework.routers import SimpleRouter

from . import views

router = SimpleRouter()
router.register(r"validation", views.ValidationViewSet, basename="validation")
router.register(r"validation-core", views.ValidationCoreViewSet, basename="validation-core")
router.register(
    r"counter-api-validation", views.CounterAPIValidationViewSet, basename="counter-api-validation"
)

urlpatterns = router.urls
