from django.conf import settings
from django.contrib.flatpages.views import flatpage
from django.contrib.sitemaps.views import sitemap
from django.urls import include, path
from django.views.decorators.vary import vary_on_cookie

from upperroom.urls import urlpatterns as ur_patterns

from .sitemaps import StaticViewSitemap

sitemaps = {
    "static": StaticViewSitemap,
}

urlpatterns = ur_patterns + [
    path("directory/", include("upperroom.directory.urls", namespace="directory")),
    path("library/", include("upperroom.library.urls", namespace="library")),
    path("poi/", include("upperroom.newsletter.urls", namespace="poi")),
    path("resources/", include("upperroom.resources.urls", namespace="resources")),
    path("roster/", include("upperroom.roster.urls", namespace="roster")),
    path("news/", include("upperroom.weblog.urls", namespace="news")),
    path("sitemap.xml", sitemap, {"sitemaps": sitemaps}, name="django.contrib.sitemaps.views.sitemap"),
    path("", vary_on_cookie(flatpage), {"url": "/"}, name="home"),
    path("calendar", vary_on_cookie(flatpage), {"url": "/calendar/"}, name="calendar"),
    path("contact", vary_on_cookie(flatpage), {"url": "/contact/"}, name="contact"),
    path("copyright", vary_on_cookie(flatpage), {"url": "/copyright/"}, name="copyright"),
]

if settings.DEBUG_TOOLBAR:
    import debug_toolbar

    urlpatterns = [path("debug/", include(debug_toolbar.urls))] + urlpatterns
