"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

API_PREFIX = "api/v1"

urlpatterns = [
    path(f"{API_PREFIX}/core/", include("core.urls")),
    path(f"{API_PREFIX}/counter/", include("counter.urls")),
    path(f"{API_PREFIX}/validations/", include("validations.urls")),
    path(f"{API_PREFIX}/auth/", include("dj_rest_auth.urls")),
    path(f"{API_PREFIX}/registration/", include("dj_rest_auth.registration.urls")),
    path(
        f"{API_PREFIX}/account/", include("django.contrib.auth.urls")
    ),  # contains link to reset password
    path("admin/", admin.site.urls),
]

if settings.DEBUG:
    import debug_toolbar

    urlpatterns += [
        path("__debug__/", include(debug_toolbar.urls)),
        *static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT),
    ]

    if "silk" in settings.INSTALLED_APPS:
        urlpatterns += [path("__silk__/", include("silk.urls", namespace="silk"))]
