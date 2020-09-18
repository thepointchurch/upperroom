from django.conf import settings
from django.contrib import admin
from django.contrib.flatpages.views import flatpage
from django.contrib.sitemaps.views import sitemap
from django.urls import include, path
from django.views.decorators.vary import vary_on_cookie

from .sitemaps import StaticViewSitemap

sitemaps = {
    "static": StaticViewSitemap,
}

urlpatterns = [
    path("directory/", include("thepoint.directory.urls", namespace="directory")),
    path("library/", include("thepoint.library.urls", namespace="library")),
    path("members/", include("thepoint.members.urls", namespace="members")),
    path("poi/", include("thepoint.newsletter.urls", namespace="poi")),
    path("resources/", include("thepoint.resources.urls", namespace="resources")),
    path("roster/", include("thepoint.roster.urls", namespace="roster")),
    path("news/", include("thepoint.weblog.urls", namespace="news")),
    path("admin/", admin.site.urls),
    path("robots.txt", include("robots.urls")),
    path("sitemap.xml", sitemap, {"sitemaps": sitemaps}, name="django.contrib.sitemaps.views.sitemap"),
    path("", vary_on_cookie(flatpage), {"url": "/"}, name="home"),
    path("calendar", vary_on_cookie(flatpage), {"url": "/calendar/"}, name="calendar"),
    path("contact", vary_on_cookie(flatpage), {"url": "/contact/"}, name="contact"),
    path("copyright", vary_on_cookie(flatpage), {"url": "/copyright/"}, name="copyright"),
]

if settings.DEBUG:
    import debug_toolbar

    urlpatterns = [path("debug/", include(debug_toolbar.urls))] + urlpatterns
