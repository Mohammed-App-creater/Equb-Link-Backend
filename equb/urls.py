
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

from owner_panel.views import EthiopianBankListView
from equbApp.views import app_config

urlpatterns = [

    path('admin/', admin.site.urls),
    # Mobile app version-check (must match both /app-config and /app-config/
    # because APPEND_SLASH 301 redirects don't preserve method on POST and
    # the client hits the bare path).
    path("app-config", app_config, name="app-config-noslash"),
    path("app-config/", app_config, name="app-config"),
        path("", include("advert.urls")),
    path(
        "",
        include("user.urls"),
    ),
        path(
        "",
        include("equbApp.urls"),
    ),
    path("api/owner/", include("owner_panel.urls")),
    # Same owner routes without api/ prefix (mobile / older clients)
    path("owner/", include("owner_panel.urls")),


    # YOUR PATTERNS
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    # Optional UI:
    path(
        "api/schema/docs/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="docs",
    ),
    path(
        "api/schema/redoc/",
        SpectacularRedocView.as_view(url_name="schema"),
        name="redoc",
    ),
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

