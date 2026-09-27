
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

urlpatterns = [

    path('admin/', admin.site.urls),
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

