from django.conf import settings
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("members/", include("upperroom.members.urls", namespace="members")),
    path("admin/", admin.site.urls),
    path("robots.txt", include("robots.urls")),
]

if settings.DEBUG_TOOLBAR:
    import debug_toolbar

    urlpatterns = [path("debug/", include(debug_toolbar.urls))] + urlpatterns
