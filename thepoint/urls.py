from django.conf.urls import include, url
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap

from .sitemaps import StaticViewSitemap

sitemaps = {
    'static': StaticViewSitemap,
}

urlpatterns = [
    url(r'^directory/', include('thepoint.apps.directory.urls', namespace='directory')),
    url(r'^library/', include('thepoint.apps.library.urls', namespace='library')),
    url(r'^members/', include('thepoint.apps.members.urls', namespace='members')),
    url(r'^poi/', include('thepoint.apps.newsletter.urls', namespace='poi')),
    url(r'^resources/', include('thepoint.apps.resources.urls', namespace='resources')),
    url(r'^roster/', include('thepoint.apps.roster.urls', namespace='roster')),

    url(r'^admin/', admin.site.urls),

    url(r'^robots\.txt', include('robots.urls')),

    url(r'^sitemap\.xml$', sitemap, {'sitemaps': sitemaps},
        name='django.contrib.sitemaps.views.sitemap'),

    url(r'', include('thepoint.apps.pages.urls', namespace='pages')),
]
