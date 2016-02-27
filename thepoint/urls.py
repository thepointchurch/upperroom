from django.conf.urls import include, url
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap

from .sitemaps import StaticViewSitemap

sitemaps = {
    'static': StaticViewSitemap,
}

urlpatterns = [
    url(r'^directory/', include('directory.urls', namespace='directory')),
    url(r'^library/', include('library.urls', namespace='library')),
    url(r'^members/', include('members.urls', namespace='members')),
    url(r'^poi/', include('newsletter.urls', namespace='poi')),
    url(r'^resources/', include('resources.urls', namespace='resources')),
    url(r'^roster/', include('roster.urls', namespace='roster')),

    url(r'^admin/', admin.site.urls),

    url(r'^robots\.txt', include('robots.urls')),

    url(r'^sitemap\.xml$', sitemap, {'sitemaps': sitemaps},
        name='django.contrib.sitemaps.views.sitemap'),

    url(r'', include('pages.urls', namespace='pages')),
]
