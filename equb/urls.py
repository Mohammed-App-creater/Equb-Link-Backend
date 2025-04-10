
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)
urlpatterns = [
    path('admin/', admin.site.urls),
        path("equb/", include("advert.urls")),
    path(
        "equb/",
        include("user.urls"),
    ),
        path(
        "equb/",
        include("equbApp.urls"),
    ),

    
    # YOUR PATTERNS
    path("equb/api/schema/", SpectacularAPIView.as_view(), name="schema"),
    # Optional UI:
    path(
        "equb/api/schema/docs/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="docs",
    ),
    path(
        "api/schema/redoc/",
        SpectacularRedocView.as_view(url_name="schema"),
        name="redoc",
    ),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
