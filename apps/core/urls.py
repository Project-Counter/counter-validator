from django.urls import path
from rest_framework.routers import SimpleRouter

from . import views

router = SimpleRouter()
router.register(r"api-key", views.UserApiKeyViewSet, basename="api-key")
router.register(r"user", views.UserManagementViewSet, basename="user")

urlpatterns = router.urls + [
    path("me", views.UserDetailView.as_view(), name="current-user"),
    path("user/password-reset", views.UserPasswordResetView.as_view(), name="user_password_reset"),
]
