from django.urls import path
from rest_framework.routers import SimpleRouter

from . import views

router = SimpleRouter()
router.register(r"api-key", views.UserApiKeyViewSet, basename="api-key")

urlpatterns = router.urls + [
    path("user", views.UserDetailView.as_view(), name="user-detail"),
]
