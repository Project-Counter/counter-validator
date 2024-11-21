from rest_framework.routers import SimpleRouter
from rest_framework_nested.routers import NestedSimpleRouter

from . import views

router = SimpleRouter()
router.register(r"validation", views.ValidationViewSet, basename="validation")
router.register(r"validation-core", views.ValidationCoreViewSet, basename="validation-core")
router.register(
    r"counter-api-validation", views.CounterAPIValidationViewSet, basename="counter-api-validation"
)

validation_router = NestedSimpleRouter(router, r"validation", lookup="validation")
validation_router.register(
    r"messages", views.ValidationMessageViewSet, basename="validation-message"
)

urlpatterns = router.urls
urlpatterns += validation_router.urls
