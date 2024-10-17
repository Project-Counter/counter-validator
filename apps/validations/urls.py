from rest_framework.routers import SimpleRouter

from . import views

router = SimpleRouter()
router.register(r"validation", views.ValidationViewSet, basename="validation")

urlpatterns = router.urls
