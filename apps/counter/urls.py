from rest_framework.routers import SimpleRouter

from . import views

router = SimpleRouter()

router.register(r"platform", views.PlatformViewSet, basename="platform")
router.register(r"sushi", views.SushiServiceViewSet, basename="sushi")

urlpatterns = router.urls
