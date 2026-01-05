
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

from wagtail.admin import urls as wagtailadmin_urls
from wagtail.documents import urls as wagtaildocs_urls
from wagtail import urls as wagtail_urls

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
    # path('cms/', include(wagtailadmin_urls)),        # CMS admin
    # path('documents/', include(wagtaildocs_urls)),   # Document serving
    # # your other app URLs
    # path('', include(wagtail_urls)), 
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

